from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from companies.models import Company
from networks.models import Network, NetworkMembership
from faker import Faker
import random

# Import signals AFTER models
from django.db.models.signals import post_save
from networks import signals

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed demo company, networks, and users for testing."

    def add_arguments(self, parser):
        parser.add_argument("--num", type=int, default=10, help="Number of networks to create")

    def handle(self, *args, **options):
        num_networks = options["num"]

        # 🔌 Disconnect signals before seeding
        post_save.disconnect(signals.membership_changed, sender=NetworkMembership)

        try:
            # 1. Create or reuse demo company
            demo_company, created = Company.objects.get_or_create(
                name="Demo Company",
                defaults={"domain": "demo.com"},
            )
            if created:
                self.stdout.write(self.style.SUCCESS("✅ Demo Company created"))
            else:
                self.stdout.write(self.style.WARNING("⚠️ Demo Company already exists, reusing it"))

            # 2. Create demo admin
            lookup_field = "username" if hasattr(User, "username") and User.USERNAME_FIELD == "username" else "email"
            lookup_value = "demo_admin" if lookup_field == "username" else "demo_admin@example.com"

            admin_defaults = {
                "is_staff": True,
                "is_superuser": False,
                "role": "admin",
                "company": demo_company,
            }

            admin, created = User.objects.get_or_create(
                **{lookup_field: lookup_value},
                defaults=admin_defaults,
            )

            if created:
                admin.password = make_password("demo1234")
                admin.save(update_fields=["password"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Demo Admin created ({lookup_field}: {lookup_value} / password: demo1234)"
                    )
                )
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Demo Admin already exists ({lookup_value})"))

            # 3. Create networks
            for _ in range(num_networks):
                network = Network.objects.create(
                    company=demo_company,
                    name=fake.company(),
                    description=fake.catch_phrase(),
                    visibility=random.choice(["company", "invite", "public"]),
                )
                NetworkMembership.objects.create(
                    network=network,
                    user=admin,
                    role="admin",
                )
                self.stdout.write(self.style.SUCCESS(f"🌐 Created network: {network.name}"))

            self.stdout.write(self.style.SUCCESS("🎉 Seeding complete!"))

        finally:
            # 🔌 Reconnect signals afterwards
            post_save.connect(signals.membership_changed, sender=NetworkMembership)



# Usage: python manage.py seed_networks --num 10
# This will create 10 networks by default, you can adjust the number with the --num argument.
# Note: Ensure that the Company, Network, NetworkMembership models and User model are correctly set up in your Django project.