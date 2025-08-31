# devices/utils.py
import nmap
from django.utils import timezone
from .models import Device, IntruderLog

def scan_network_and_log_intruders():
    nm = nmap.PortScanner()
    # Adjust subnet to your network range
    nm.scan(hosts="192.168.1.0/24", arguments="-sn")  # Ping scan

    for host in nm.all_hosts():
        mac = nm[host]['addresses'].get('mac', None)
        ip = nm[host]['addresses'].get('ipv4', None)

        if mac:
            # Check if this MAC is in the registered devices
            registered = Device.objects.filter(mac_address__iexact=mac).exists()

            if not registered:
                IntruderLog.objects.create(
                    ip_address=ip,
                    mac_address=mac,
                    detected_at=timezone.now()
                )



from django.core.mail import send_mail

def scan_network():
    results = scan_network_and_log_intruders()  # Your existing scan function
    intruders = [device for device in results if device["status"] == "intruder"]

    if intruders:
        message = "\n".join([f"{d['ip']} ({d['mac']})" for d in intruders])
        send_mail(
            subject="Intruder Detected on Network",
            message=f"Intruder(s) found:\n\n{message}",
            from_email=None,
            recipient_list=["admin@example.com"],
            fail_silently=False,
        )

    return results
