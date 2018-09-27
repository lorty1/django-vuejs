from django.core.management.base import BaseCommand, CommandError
from simpleproduct.models import Product

class Command(BaseCommand):
    help = 'Actualize every muscle temp weight with its real weight'

    def handle(self, *args, **options):
        products = Product.objects.filter(category__slug='stock')
        for p in products:
            p.temp_number = p.number
            p.save()
        products = Product.objects.filter(category__slug='dry')
        for p in products:
            p.temp_number = p.number
            p.save()
            #self.stdout.write(self.style.SUCCESS('Successfully actualized muscles "%s"' % m.id))
