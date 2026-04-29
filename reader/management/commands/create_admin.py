from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Create default admin user"

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@speedreader.com',
                password='ChangeMe123!'
            )
            self.stdout.write(self.style.SUCCESS("✓ Admin created!"))
        else:
            self.stdout.write("· Admin already exists.")