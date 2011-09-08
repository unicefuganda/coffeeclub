from django.db import models
from rapidsms.models import Contact
from django.contrib.auth.models import Group
from script.signals import script_progress_was_completed
from script.models import ScriptSession
from script.utils.handling import find_closest_match, find_best_response
from poll.models import YES_WORDS
from rapidsms_xforms.models import XFormField, XForm, XFormSubmission, dl_distance, xform_received
import datetime
from django.template import Template, Context
from django.core.mail import send_mail

class Department(Group):
    floor = models.CharField(max_length=15, blank=True)

class MenuItem(models.Model):
    name = models.CharField(max_length=50, blank=True)
    cost = models.IntegerField(max_length=10, blank=True, null=True)
    def __unicode__(self):
        return self.name

class CustomerPref(models.Model):
    milk_type_choices = (('either', 'Either'), ('low fat', 'Low Fat'), ('whole', 'Whole'))
    running_order = models.BooleanField(default=False, blank=True)
    standard_drink = models.ForeignKey(MenuItem, blank=True, null=True)
    milk_type = models.CharField(max_length=50, choices=milk_type_choices, blank=True, null=True)
    #TODO naming is a bit off (Which days per week?)
    days_on_call = models.CharField(max_length=200, blank=True, null=True)
    own_cup = models.BooleanField(default=False, blank=True)
    notes = models.TextField(blank=True, null=True)

class Customer(Contact):
    preferences = models.ForeignKey(CustomerPref, related_name='preferences', null=True)
    extension = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)

    def in_negative(self):
        return self.accounts.filter(balance_lt=0)

    def account_bal(self):
        return self.accounts.all()[0].balance

    def send_email(self, context={}, type=False):
        recipients = list(self.email)
        msg = Email.objects.filter(email_type=type)[0] if type else Email.objects.filter(email_type='alert')[0]
        subject_template = Template(msg.subject)
        message_template = Template(msg.message)
        ctxt = Context(context)
        subject = subject_template.render(ctxt)
        message = message_template.render(ctxt)
        if message.strip():
            send_mail(subject, message, msg.sender, recipients, fail_silently=False)

    def save(self, force_insert=False, force_update=False, using=False):
        if self.preferences is None:
            self.preferences = CustomerPref.objects.create()
        super(Customer, self).save(force_insert, force_update)

class CoffeeOrder(models.Model):
    date = models.DateTimeField()
    customer = models.ForeignKey(Customer, related_name="order")
    coffee_name = models.ForeignKey(MenuItem, blank=True, null=True)
    num_cups = models.IntegerField(max_length=2)
    deliver_to = models.CharField(max_length=100, blank=True, null=True)

class Account(models.Model):
    owner = models.ForeignKey(Customer, related_name="accounts")
    balance = models.IntegerField(max_length=10, default=0)
    date_updated = models.DateTimeField(auto_now=True)

class Email(models.Model):
    email_type_choices = (('alert', 'Balance Alert'), ('marketing', 'Marketing'))
    subject = models.TextField()
    sender = models.EmailField(default='no-reply@uganda.rapidsms.org')
    message = models.TextField()
    email_type = models.CharField(max_length=10, default='alert', choices=email_type_choices, blank=True, null=True)

def coffee_autoreg(**kwargs):

    connection = kwargs['connection']
    progress = kwargs['sender']
    if not progress.script.slug == 'coffee_autoreg':
        return

    session = ScriptSession.objects.filter(script=progress.script, connection=connection).order_by('-end_time')[0]
    script = progress.script

    name_poll = script.steps.get(order=1).poll
    department_poll = script.steps.get(order=2).poll
    extension_poll = script.steps.get(order=3).poll
    email_poll = script.steps.get(order=4).poll
    coffee_standard_poll = script.steps.get(order=5).poll
    milktype_poll = script.steps.get(order=6).poll
    running_order_poll = script.steps.get(order=7).poll
    own_cup_poll = script.steps.get(order=8).poll
    other_notes_poll = script.steps.get(order=9).poll

    if not connection.contact:
            connection.contact = Customer.objects.create()
            connection.save()
    contact = connection.contact

    name = find_best_response(session, name_poll)
    if name:
        name = ' '.join([n.capitalize() for n in name.lower().split(' ')])
        contact.name = name[:100]

    department = find_best_response(session, department_poll)
    if department:
        group = find_closest_match(department, Group.objects)
        if not group:
            group = Group.objects.get(name='Other Coffee People')
    contact.groups.add(group)

    extension = find_best_response(session, extension_poll)
    contact.extension = extension

    email = find_best_response(session, email_poll)
    contact.email = email
    contact.save()

    prefs = contact.preferences
    drink = find_best_response(session, coffee_standard_poll)
    if drink:
        prefs.standard_drink = find_closest_match(drink, MenuItem.objects)

    milktype = find_best_response(session, milktype_poll)
    if milktype:
        milktype = ' '.join([n.capitalize() for n in milktype.lower().split(' ')])
        prefs.milk_type = milktype

    own_cup = find_best_response(session, own_cup_poll)
    if own_cup and own_cup in YES_WORDS:
        prefs.own_cup = True

    notes = find_best_response(session, other_notes_poll)
    if notes:
        notes = ' '.join([n.capitalize() for n in notes.lower().split(' ')])
        prefs.notes = notes

    prefs.save()
    Account.objects.create(owner=contact)

def xform_received_handler(sender, **kwargs):
    xform = kwargs['xform']
    submission = kwargs['submission']
    contact = Contact.objects.get(pk=kwargs['message'].connection.contact_id)

    if xform.keyword == 'coffee':
        date = datetime.datetime.now()
        customer = Customer.objects.filter(pk=contact.pk)[0]
        if submission.eav.coffee_type:
            coffee_name = find_closest_match(submission.eav.coffee_type, MenuItem.objects)
        else:
            coffee_name = customer.preferences.standard_drink
        if submission.eav.coffee_location:
            deliver_to = submission.eav.coffee_location
        else:
            deliver_to = contact.groups.all()[0].name + ' ' + Department.objects.get(pk=contact.groups.all()[0].pk).floor

        num_cups = submission.eav.coffee_cups if submission.eav.coffee_cups else 1

        CoffeeOrder.objects.create(\
            date=date, \
            customer=customer, \
            coffee_name=coffee_name, \
            num_cups=num_cups, \
            deliver_to=deliver_to, \
            )
        submission.response = str(num_cups) + ' cup(s) of ' + coffee_name.name + ' coming up shortly! We will deliver to ' + deliver_to
        submission.save()

script_progress_was_completed.connect(coffee_autoreg, weak=False)
xform_received.connect(xform_received_handler, weak=False)



