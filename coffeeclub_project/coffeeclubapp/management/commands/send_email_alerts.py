import datetime

from django.core.management.base import BaseCommand
from script.models import *

from rapidsms.models import Backend, Connection, Contact
from rapidsms_httprouter.models import Message
from coffeeclubapp.utils import send_template_email
from django.core.mail import send_mail
from coffeeclubapp.models import Email
class Command(BaseCommand):

    help = """send an queued emails """


    def handle(self, **options):
        context=dict(subject=email.subject,message=message,)
        emails_to_send=EmailAlert.objects.filter(sent=False,date_to_send__ge=datetime.now())
        for email in emails_to_send:
            if email.customer.preferences.email:
                send_template_email([email.customer.prefrences.email], "coffeeclubapp/email_template.html", context)

