# alerts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import IntruderLog
from devices.models import Device

@receiver(post_save, sender=IntruderLog)
def link_intruder_to_device(sender, instance, created, **kwargs):
    if created and not instance.device and instance.mac_address:
        try:
            device = Device.objects.get(mac_address=instance.mac_address)
            instance.device = device
            instance.save(update_fields=["device"])
        except Device.DoesNotExist:
            pass
