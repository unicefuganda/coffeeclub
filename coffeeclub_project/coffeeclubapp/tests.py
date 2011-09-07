"""
Basic tests for coffeeclub app
"""
from django.test import TestCase
from django.contrib.auth.models import User, Group
from rapidsms.messages.incoming import IncomingMessage
from rapidsms_xforms.models import *
from rapidsms_httprouter.models import Message
import datetime
from rapidsms.models import Connection, Backend, Contact
from rapidsms.messages.incoming import IncomingMessage
from rapidsms_xforms.models import XForm, XFormSubmission
from django.conf import settings
from script.utils.outgoing import check_progress
from script.models import Script, ScriptProgress, ScriptSession, ScriptResponse
from rapidsms_httprouter.router import get_router
from script.signals import script_progress_was_completed, script_progress
from poll.management import create_attributes
from .management import init_groups, init_xforms, init_autoreg
from .models import MenuItem, CustomerPref, Customer, CoffeeOrder, Account, Department
from django.db import connection

class ModelTest(TestCase): #pragma: no cover

    def fake_incoming(self, message, connection=None):
        if connection is None:
            connection = self.connection
        router = get_router()
        router.handle_incoming(connection.backend.name, connection.identity, message)
        form = XForm.find_form(message)
        if form:
            return XFormSubmission.objects.all().order_by('-created')[0]


    def spoof_incoming_obj(self, message, connection=None):
        if connection is None:
            connection = Connection.objects.all()[0]
        incomingmessage = IncomingMessage(connection, message)
        incomingmessage.db_message = Message.objects.create(direction='I', connection=Connection.objects.all()[0], text=message)
        return incomingmessage


    def assertResponseEquals(self, message, expected_response, connection=None):
        s = self.fake_incoming(message, connection)
        self.assertEquals(s.response, expected_response)


    def fake_submission(self, message, connection=None):
        form = XForm.find_form(message)
        if connection is None:
            try:
                connection = Connection.objects.all()[0]
            except IndexError:
                backend, created = Backend.objects.get_or_create(name='test')
                connection, created = Connection.objects.get_or_create(identity='8675309',
                                                                       backend=backend)
        # if so, process it
        incomingmessage = IncomingMessage(connection, message)
        incomingmessage.db_message = Message.objects.create(direction='I', connection=connection, text=message)
        if form:
            submission = form.process_sms_submission(incomingmessage)
            return submission
        return None


    def fake_error_submission(self, message, connection=None):
        form = XForm.find_form(message)

        if connection is None:
            connection = Connection.objects.all()[0]
        # if so, process it
        incomingmessage = IncomingMessage(connection, message)
        incomingmessage.db_message = Message.objects.create(direction='I', connection=Connection.objects.all()[0], text=message)
        if form:
            submission = form.process_sms_submission(incomingmessage)
            self.failUnless(submission.has_errors)
        return

    def elapseTime(self, submission, seconds):
        newtime = submission.created - datetime.timedelta(seconds=seconds)
        cursor = connection.cursor()
        cursor.execute("update rapidsms_xforms_xformsubmission set created = '%s' where id = %d" %
                       (newtime.strftime('%Y-%m-%d %H:%M:%S.%f'), submission.pk))

    def fake_script_dialog(self, script_prog, connection, responses, emit_signal=True):
        script = script_prog.script
        ss = ScriptSession.objects.create(script=script, connection=connection, start_time=datetime.datetime.now())
        for poll_name, resp in responses:
            poll = script.steps.get(poll__name=poll_name).poll
            poll.process_response(self.spoof_incoming_obj(resp))
            resp = poll.responses.all().order_by('-date')[0]
            ScriptResponse.objects.create(session=ss, response=resp)
        ss.end_time = datetime.datetime.now()
        ss.save()
        if emit_signal:
            script_progress_was_completed.send(connection=connection, sender=script_prog)
        return ss

    def setUp(self):
        if 'django.contrib.sites' in settings.INSTALLED_APPS:
            site_id = getattr(settings, 'SITE_ID', 1)
            Site.objects.get_or_create(pk=site_id, defaults={'domain':'rapidcoffee.com'})
        init_groups()
        init_xforms(None)
        init_autoreg(None)
        create_attributes()
        User.objects.get_or_create(username='admin')
        self.backend = Backend.objects.create(name='test')
        self.connection = Connection.objects.create(identity='8675309', backend=self.backend)
        grp = Group.objects.get(name='T4D')
        self.department = Department.objects.create(pk=grp.pk)
        self.department.floor = '2nd Floor'
        self.department.save()
        grp.floor = '2nd Floor'
        grp.save()
        self.expresso = MenuItem.objects.create(name='Expresso', cost=2500)
        self.cappuccino = MenuItem.objects.create(name='Capuccino', cost=2500)

    def testBasicAutoReg(self):
        self.fake_incoming('join')
        self.assertEquals(ScriptProgress.objects.count(), 1)
        script_prog = ScriptProgress.objects.all()[0]
        self.assertEquals(script_prog.script.slug, 'coffee_autoreg')

        self.fake_script_dialog(script_prog, self.connection, [\
            ('coffee_drinker', 'moses mugisha'), \
            ('coffee_department', 'T4D'), \
            ('coffee_extension', '1760'), \
            ('coffee_email', 'mossplix@yahoo.com'), \
            ('coffee_standard_type', 'expresso'), \
            ('coffee_milktype', 'cow milk'), \
            ('coffee_running_order', 'Mon, Tue, Wednesday, Thur'), \
            ('coffee_own_cup', 'no'), \
            ('coffee_other_notes', 'add some sugar'), \
        ])
        self.assertEquals(Customer.objects.count(), 1)
        contact = Customer.objects.all()[0]
        self.assertEquals(contact.name, 'Moses Mugisha')
        self.assertEquals(contact.groups.all()[0].name, 'T4D')
        self.assertEquals(Department.objects.get(pk=contact.groups.all()[0].pk).floor, '2nd Floor')
        self.assertEquals(contact.extension, '1760')
        self.assertEquals(contact.email, 'mossplix@yahoo.com')
        prefs = contact.preferences
        self.assertEquals(prefs.standard_drink.name, 'Expresso')
        self.assertEquals(prefs.milk_type, 'Cow Milk')
#        self.assertEquals(contact.running_order, True)
        self.assertEquals(prefs.own_cup, False)
        self.assertEquals(prefs.notes, 'Add Some Sugar')
        self.assertEquals(Account.objects.all()[0].owner, contact)

    def testBasicCoffeeOrder(self):

        self.fake_incoming('join')
        self.assertEquals(ScriptProgress.objects.count(), 1)
        script_prog = ScriptProgress.objects.all()[0]
        self.assertEquals(script_prog.script.slug, 'coffee_autoreg')

        self.fake_script_dialog(script_prog, self.connection, [\
            ('coffee_drinker', 'moses mugisha'), \
            ('coffee_department', 'T4D'), \
            ('coffee_extension', '1760'), \
            ('coffee_email', 'mossplix@yahoo.com'), \
            ('coffee_standard_type', 'xpresso'), \
            ('coffee_milktype', 'cow milk'), \
            ('coffee_running_order', 'Mon, Tue, Wednesday, Thur'), \
            ('coffee_own_cup', 'no'), \
            ('coffee_other_notes', 'add some sugar'), \
        ])

        self.fake_incoming('coffee 2')
        contact = Customer.objects.all()[0]
        coffee_order = CoffeeOrder.objects.order_by('-date').filter(customer=contact)[0]
        self.assertEquals(coffee_order.num_cups, 2)
        self.assertEquals(coffee_order.coffee_name, self.expresso)

        self.fake_incoming('coffee')
        coffee_order = CoffeeOrder.objects.order_by('-date').filter(customer=contact)[0]
        self.assertEquals(coffee_order.num_cups, 1)

        self.fake_incoming('coffee 2 Western Conference Room')
        coffee_order = CoffeeOrder.objects.order_by('-date').filter(customer=contact)[0]
        self.assertEquals(coffee_order.num_cups, 2)
        self.assertEquals(coffee_order.deliver_to, 'Western Conference Room')


