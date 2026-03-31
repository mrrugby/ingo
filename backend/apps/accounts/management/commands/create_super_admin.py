from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import UserRole


class Command(BaseCommand):
    help = "Create a super admin account for INGO."

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True)
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)

    def handle(self, *args, **options):
        user_model = get_user_model()
        email = options["email"].lower()

        if user_model.objects.filter(email=email).exists():
            raise CommandError("A user with that email already exists.")

        user_model.objects.create_superuser(
            email=email,
            password=options["password"],
            full_name=options["name"],
            role=UserRole.SUPER_ADMIN,
        )
        self.stdout.write(self.style.SUCCESS("Super admin created successfully."))

