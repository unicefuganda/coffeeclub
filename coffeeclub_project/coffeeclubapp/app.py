from rapidsms.apps.base import AppBase
from script.models import Script, ScriptProgress
from django.conf import settings
from unregister.models import Blacklist
from coffeeclubapp.models import Customer

class App (AppBase):

    def handle (self, message):
        if message.text.strip().lower() in [i.lower() for i in getattr(settings, 'OPT_OUT_WORDS', [])]:
            Blacklist.objects.create(connection=message.connection)
            if (message.connection.contact):
                customer = Customer.objects.get(pk=message.connection.contact.pk)
                message.connection.contact.active = False
                message.connection.contact.save()
                customer.active = False
                customer.save()
            message.respond(getattr(settings, 'OPT_OUT_CONFIRMATION', 'Thank you for using being a part of the Coffee Club. If you ever want to rejoin the Coffee Club send JOIN to 6767'))
            return True
        elif message.text.strip().lower() in [i.lower() for i in getattr(settings, 'OPT_IN_WORDS', [])]:
            if Blacklist.objects.filter(connection=message.connection).count() or not message.connection.contact:
                for b in Blacklist.objects.filter(connection=message.connection):
                    b.delete()
                if not message.connection.contact and \
                not ScriptProgress.objects.filter(script__slug='coffee_autoreg', connection=message.connection).count():
                    ScriptProgress.objects.create(script=Script.objects.get(slug="coffee_autoreg"), \
                                          connection=message.connection)
            else:
                message.repond("You are already in the system and do not need to 'Join' again.")
            return True
        elif Blacklist.objects.filter(connection=message.connection).count():
            return True
        return False
