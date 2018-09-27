from django.core.management.base import BaseCommand, CommandError
from easycheckout.models import Order

class Command(BaseCommand):
    help = 'Delete once a day order unsuccessfull orders'

    def handle(self, *args, **options):
        orders = Order.objects.exclude(payment_status="Success")
        for p in orders:
            p.delete()
