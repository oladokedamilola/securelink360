from django.core.management.base import BaseCommand
from devices.utils import scan_network_and_detect_intruders

class Command(BaseCommand):
    help = "Scan the network and log intruders"

    def add_arguments(self, parser):
        parser.add_argument(
            "--target", type=str, default="192.168.1.0/24",
            help="Target IP range to scan"
        )

    def handle(self, *args, **options):
        target_ip = options["target"]
        self.stdout.write(self.style.WARNING(f"Scanning network: {target_ip}"))

        devices = scan_network_and_detect_intruders(target_ip)

        self.stdout.write(self.style.SUCCESS(f"Scan completed. {len(devices)} devices found."))
