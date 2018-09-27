from django.core.management.base import BaseCommand, CommandError
from simpleproduct.models import Muscle

class Command(BaseCommand):
    help = 'Actualize every muscle temp weight with its real weight'

    def handle(self, *args, **options):
        muscles = Muscle.objects.filter(cow__is_active=True)
        for m in muscles:
            m.reset_temp_weight()
            #self.stdout.write(self.style.SUCCESS('Successfully actualized muscles "%s"' % m.id))
