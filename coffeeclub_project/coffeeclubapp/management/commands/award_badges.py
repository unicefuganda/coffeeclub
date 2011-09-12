import datetime

from django.core.management.base import BaseCommand
import calendar
from datetime import calendar
class Command(BaseCommand):

    help = """send an queued emails """


    def handle(self, **options):
        """award weekly/monthly/alltime badges"""
        #if its saturday, award weekly leader badge (bronze) and notify (schedule it for monday)
        today=datetime.now()
        if calendar.weekday(today.year, today.month, todayday) == 5:
            weekly_lead=





        # if it is end of the month, award monthly leader (silver) and notify

        #if the current overall leader is overtaken, reaward  and notify
