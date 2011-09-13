from django.core.management.base import BaseCommand
from coffeeclubapp.utils import handle_excel_file
from optparse import OptionParser, make_option

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--file", dest="filename", help='Excel File to read'),
    )

    def handle(self, **options):
        handle_excel_file(file=open(options['filename']))
        self.stdout.write('Successfully imported file')

