import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Network, NetworkMembership
from accounts.models import User

def group_name_for_network(network_id: int) -> str:
    return f"network_{network_id}"

def group_name_for_company(company_id: int) -> str:
    return f"company_{company_id}"

class NetworkConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.scope_user = self.scope.get("user", AnonymousUser())
        # URL can be /ws/network/<id>/ or /ws/company/<id>/
        self.network_id = self.scope["url_route"]["kwargs"].get("network_id")
        self.company_id = self.scope["url_route"]["kwargs"].get("company_id")
        self.group_name = None

        if not self.scope_user.is_authenticated:
            await self.close(code=4001)
            return

        if self.network_id:
            # Check user can view this network
            allowed = await self.user_can_view_network(self.scope_user.id, self.network_id)
            if not allowed:
                await self.close(code=4003)
                return
            self.group_name = group_name_for_network(self.network_id)

        elif self.company_id:
            # Check user belongs to company
            if not hasattr(self.scope_user, "company") or not self.scope_user.company or self.scope_user.company_id != int(self.company_id):
                await self.close(code=4003)
                return
            self.group_name = group_name_for_company(self.company_id)

        else:
            await self.close(code=4002)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Optional: send initial snapshot
        initial = await self.initial_snapshot()
        await self.send_json({"type": "snapshot", **initial})

    async def disconnect(self, code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Clients can send simple commands: e.g., {"action": "acknowledge_intruder", "attempt_id": 123}
        if not text_data:
            return
        data = json.loads(text_data)
        action = data.get("action")

        if action == "acknowledge_intruder":
            attempt_id = data.get("attempt_id")
            await self.mark_intruder_acknowledged(attempt_id)

        elif action == "escalate_intruder":
            attempt_id = data.get("attempt_id")
            note = data.get("note", "")
            await self.escalate_intruder(attempt_id, note)

    async def broadcast(self, event):
        # Called by channel_layer.group_send
        await self.send_json(event["payload"])

    async def send_json(self, payload: dict):
        await self.send(text_data=json.dumps(payload))

    @database_sync_to_async
    def user_can_view_network(self, user_id: int, network_id: int) -> bool:
        try:
            nm_exists = NetworkMembership.objects.filter(user_id=user_id, network_id=network_id, active=True).exists()
            if nm_exists:
                return True
            # Admins can view all networks in their company
            u = User.objects.get(id=user_id)
            n = Network.objects.get(id=network_id)
            return u.company_id == n.company_id and u.is_company_admin()
        except Exception:
            return False

    @database_sync_to_async
    def initial_snapshot(self) -> dict:
        """
        Return nodes and edges for initial graph.
        Nodes: users, devices, intruder placeholders (none initially)
        """
        from devices.models import Device
        from alerts.models import IntruderLog

        if self.network_id:
            n = Network.objects.get(id=self.network_id)
            members = list(n.memberships.select_related("user").values(
                "user_id", "user__email", "role"
            ))
            devices = list(Device.objects.filter(company=n.company).values("id", "name", "ip_address"))
            # Recent unresolved intruders (optional)
            intruders = list(IntruderLog.objects.filter(
                unauthorized_attempt__network=n, status="Detected"
            ).values("id", "ip_address", "mac_address"))
        else:
            # company scope
            from companies.models import Company
            c_id = int(self.company_id)
            members = list(NetworkMembership.objects.filter(network__company_id=c_id)
                           .select_related("user").values("user_id", "user__email", "role"))
            devices = list(Device.objects.filter(company_id=c_id).values("id", "name", "ip_address"))
            intruders = []

        return {
            "nodes": {
                "users": members,
                "devices": devices,
                "intruders": intruders
            },
            "edges": []  # you can compute edges (user->device) from your domain if needed
        }

    @database_sync_to_async
    def mark_intruder_acknowledged(self, attempt_id: int):
        from alerts.models import IntruderLog
        log = IntruderLog.objects.filter(unauthorized_attempt_id=attempt_id).first()
        if log:
            log.status = "Acknowledged"
            log.save()

    @database_sync_to_async
    def escalate_intruder(self, attempt_id: int, note: str):
        from alerts.models import IntruderLog
        log = IntruderLog.objects.filter(unauthorized_attempt_id=attempt_id).first()
        if log:
            log.status = "Escalated"
            log.save()
            # Optional: create a ticket or send email/slack
