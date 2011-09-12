import datetime

from django.core.management.base import BaseCommand
class Command(BaseCommand):

    help = """send an queued emails """


    def handle(self, **options):
        """award weekly/monthly/alltime badges"""
