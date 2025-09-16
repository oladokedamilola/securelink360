# networks/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Network, NetworkMembership, JoinRequest, Device
from alerts.models import IntruderLog

class NetworkVisualizationConsumer(AsyncWebsocketConsumer):
    """Handles WebSocket connections for admins monitoring a network."""
    
    async def connect(self):
        self.network_id = self.scope['url_route']['kwargs']['network_id']
        self.network_group_name = f'network_{self.network_id}_monitors'
        self.user = self.scope["user"]

        # Check if user is authenticated
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        # Check if user is authorized (admin of this network)
        is_authorized = await self.is_user_network_admin(self.user, self.network_id)
        if not is_authorized:
            await self.close()
            return

        # Join the network group
        await self.channel_layer.group_add(
            self.network_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"Admin {self.user.email} connected to monitor network {self.network_id}")

        # Send initial state
        initial_state = await self.get_initial_state(self.network_id)
        await self.send(text_data=json.dumps({
            'type': 'initial_state',
            'data': initial_state
        }))

    async def disconnect(self, close_code):
        # Leave the network group
        await self.channel_layer.group_discard(
            self.network_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def is_user_network_admin(self, user, network_id):
        """Check if the user is an admin of this specific network."""
        try:
            membership = NetworkMembership.objects.get(
                network_id=network_id,
                user=user
            )
            return membership.role == 'admin'
        except NetworkMembership.DoesNotExist:
            return False

    @database_sync_to_async
    def get_initial_state(self, network_id):
        """Get the initial state of the network."""
        network = Network.objects.get(id=network_id)
        devices = Device.objects.filter(user__company=network.company)
        pending_requests = JoinRequest.objects.filter(network_id=network_id, status="pending")
        
        return {
            'devices': [
                {
                    'id': device.id,
                    'name': device.name,
                    'mac_address': device.mac_address,
                    'status': device.status,
                    'user_email': device.user.email if device.user else 'Unassigned'
                }
                for device in devices
            ],
            'pending_requests': [
                {
                    'id': req.id,
                    'user_email': req.user.email,
                    'device_name': req.device.name if req.device else 'No device',
                    'ip_address': req.ip_address,
                    'created_at': req.created_at.isoformat()
                }
                for req in pending_requests
            ],
            'network': {
                'name': network.name,
                'description': network.description
            }
        }

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        
        if message_type == 'approve_request':
            await self.approve_join_request(text_data_json['request_id'])
        elif message_type == 'reject_request':
            await self.reject_join_request(text_data_json['request_id'])

    # Receive message from room group
    async def network_message(self, event):
        """Send message to WebSocket."""
        message = event['message']
        await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def approve_join_request(self, request_id):
        """Approve a join request."""
        jr = JoinRequest.objects.get(id=request_id)
        jr.status = "approved"
        jr.save()

        # Add user to network
        NetworkMembership.objects.get_or_create(
            user=jr.user,
            network=jr.network,
            defaults={"role": "employee", "active": True}
        )

        # Update device status
        if jr.device:
            jr.device.status = "online"
            jr.device.save()

        # Notify the user who was approved
        self.channel_layer.group_send(
            f'user_{jr.user.id}',
            {
                'type': 'user_message',
                'message': {
                    'type': 'request_approved',
                    'request_id': jr.id,
                    'network_name': jr.network.name
                }
            }
        )

    @database_sync_to_async
    def reject_join_request(self, request_id):
        """Reject a join request."""
        jr = JoinRequest.objects.get(id=request_id)
        jr.status = "rejected"
        jr.save()

        # Notify the user who was rejected
        self.channel_layer.group_send(
            f'user_{jr.user.id}',
            {
                'type': 'user_message',
                'message': {
                    'type': 'request_rejected', 
                    'request_id': jr.id,
                    'network_name': jr.network.name
                }
            }
        )


class NetworkJoinConsumer(AsyncWebsocketConsumer):
    """Handles WebSocket connections for users requesting to join a network."""
    
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        """Receive join request from user."""
        try:
            text_data_json = json.loads(text_data)
            network_id = text_data_json.get('network_id')
            device_id = text_data_json.get('device_id')
            
            response = await self.process_join_request(
                self.scope["user"], network_id, device_id
            )
            
            await self.send(text_data=json.dumps(response))
            
            # If it's a new request, notify admin group
            if response.get('status') in ['pending', 'intruder_detected']:
                await self.notify_admin_group(network_id, response)
                
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    @database_sync_to_async
    def process_join_request(self, user, network_id, device_id):
        """Process the join request in database."""
        try:
            network = Network.objects.get(id=network_id)
        except Network.DoesNotExist:
            return {'type': 'error', 'message': 'Network not found.'}

        # Check if user is part of the network's company
        if user.company != network.company and network.visibility != 'public':
            # INTRUDER DETECTED!
            intruder_log = IntruderLog.objects.create(
                user=user,
                ip_address=self.get_client_ip(),
                note=f"Attempted to join network '{network.name}' without proper access."
            )
            return {
                'type': 'join_response',
                'status': 'intruder_detected',
                'message': 'Access denied. Your attempt has been logged.'
            }

        # Check for existing request
        existing_request = JoinRequest.objects.filter(
            network=network, user=user, status="pending"
        ).first()
        
        if existing_request:
            return {
                'type': 'join_response',
                'status': existing_request.status,
                'message': f'You already have a {existing_request.status} request for this network.'
            }

        # Create new join request
        device = None
        if device_id:
            try:
                device = Device.objects.get(id=device_id, user=user)
                device.status = "pending"
                device.save()
            except Device.DoesNotExist:
                pass

        join_request = JoinRequest.objects.create(
            network=network,
            user=user,
            device=device,
            ip_address=self.get_client_ip(),
            status="pending"
        )

        return {
            'type': 'join_response',
            'status': 'pending',
            'message': 'Your request has been sent for approval.',
            'request_id': join_request.id
        }

    def get_client_ip(self):
        """Get client IP address from scope."""
        x_forwarded_for = self.scope.get('headers', [])
        for header, value in x_forwarded_for:
            if header == b'x-forwarded-for':
                return value.decode('utf-8').split(',')[0].strip()
        return self.scope['client'][0]

    async def notify_admin_group(self, network_id, response_data):
        """Notify admin group about new join request or intrusion."""
        network_group_name = f'network_{network_id}_monitors'
        
        message = {
            'type': 'join_request_new',
            'data': {
                **response_data,
                'ip_address': self.get_client_ip(),
                'user_email': self.scope["user"].email,
            }
        }

        await self.channel_layer.group_send(
            network_group_name,
            {
                'type': 'network.message',
                'message': message
            }
        )