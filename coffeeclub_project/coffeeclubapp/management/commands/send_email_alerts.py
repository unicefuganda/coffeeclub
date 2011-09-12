import datetime

from django.core.management.base import BaseCommand

from coffeeclubapp.utils import send_template_email
from coffeeclubapp.models import EmailAlert
class Command(BaseCommand):

    help = """send an queued emails """


    def handle(self, **options):

        emails_to_send=EmailAlert.objects.filter(sent=False,date_to_send__ge=datetime.now())
        for e in emails_to_send:
            context=dict(subject=e.subject,content=e.content,)
            if e.customer.preferences.email:
                send_template_email([e.customer.prefrences.email], "coffeeclubapp/email_template.html", context)

