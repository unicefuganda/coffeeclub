import datetime

from django.core.management.base import BaseCommand
import calendar
from datetime import calendar
from coffeeclub_project.coffeeclubapp.models import Award

class Command(BaseCommand):

    help = """send an queued emails """


    def handle(self, **options):
        """award weekly/monthly/alltime badges"""
        #if its saturday, award weekly leader badge (bronze) and notify (schedule it for monday)
        today=datetime.now()
        if calendar.weekday(today.year, today.month, todayday) == calendar.SATURDAY:
            weekly_lead=CoffeeOrder.objects.filter(date__range=(week_ago,today)).values('customer__name',
                                                                 'customer__pk').annotate(ccount=Count\
                    ('num_cups')).order_by('-ccount')[0]
            badge=Badge.objects.get(type=Badge.BRONZE)
            customer=get_object_or_404(Customer,pk=weekly_lead['customer__pk'])
            Award.objects.create(customer=customer,badge=badge)


        # if it is end of the month, award monthly leader (silver) and notify

        #if the current overall leader is overtaken, reaward  and notify
