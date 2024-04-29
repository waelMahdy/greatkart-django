from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Account

class Command(BaseCommand):
    help = 'Create a superuser if one does not exist'

    def handle(self, *args, **options):
        if not Account.objects.filter(username='wael').exists():
            Account.objects.create_superuser('wael', 'mahdy', 'wael',  '1234','wael@gmail.com')
            self.stdout.write(self.style.SUCCESS('Successfully created a new superuser'))
        else:
            self.stdout.write(self.style.WARNING('A superuser already exists'))
