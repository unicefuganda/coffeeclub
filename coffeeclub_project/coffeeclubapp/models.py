from django.db import models
from django.db.models.signals import post_save
from rapidsms.models import Contact
from django.contrib.auth.models import Group
from script.signals import script_progress_was_completed
from script.models import ScriptSession
from script.utils.handling import find_closest_match, find_best_response
from poll.models import YES_WORDS
from rapidsms_xforms.models import XFormField, XForm, XFormSubmission, dl_distance, xform_received
from django.template import Template, Context
from django.core.mail import send_mail
from datetime import datetime,timedelta
from django.db.models.signals import post_save
from decimal import Decimal
class Department(Group):
    floor = models.CharField(max_length=15, blank=True)

class MenuItem(models.Model):
    name = models.CharField(max_length=50, blank=True)
    cost = models.DecimalField(max_digits=10, blank=True, null=True,decimal_places=2)
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
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.preferences is None:
            self.preferences = CustomerPref.objects.create()
        super(Customer, self).save(*args, **kwargs)

    def negative_bal(self):
        return self.accounts.all()[0].balance < 0

    def account_bal(self):
        return self.accounts.all()[0].balance

    def send_email(self, context={}, type=False):
        recipients = list(self.email)
        msg = MessageContent.objects.filter(type=type)[0] if type else MessageContent.objects.filter(type='alert')[0]
        subject_template = Template(msg.subject)
        message_template = Template(msg.message)
        ctxt = Context(context)
        subject = subject_template.render(ctxt)
        message = message_template.render(ctxt)
        if message.strip():
            send_mail(subject, message, msg.sender, recipients, fail_silently=False)

    #def __unicode__(self):
    #   return self.name + ' ' + lambda self.groups.all():.name


    def save(self,*args,**kwargs):
        if self.preferences is None:
            self.preferences = CustomerPref.objects.create()
        super(Customer, self).save(*args, **kwargs)

class Account(models.Model):
    customer = models.ForeignKey(Customer, related_name="accounts")
    balance = models.DecimalField(max_digits=10, default=0.00,decimal_places=2)
    date_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return str(self.balance)

class CoffeeOrder(models.Model):
    date = models.DateTimeField(default=datetime.now())
    customer = models.ForeignKey(Customer, related_name="order")
    coffee_name = models.ForeignKey(MenuItem, blank=True, null=True)
    num_cups = models.IntegerField(max_length=2)
    deliver_to = models.CharField(max_length=100, blank=True, null=True)
    def cost(self):
        try:
            if self.coffee_name and self.coffee_name.cost:
                return self.num_cups*self.coffee_name.cost
            else:
                return self.num_cups*2500.00
        except ValueError:
            return float(self.coffee_name.cost)

#send low balance and update account balance notifications
def check_balance_handler(sender, **kwargs):
    instance = kwargs['instance']
    account=instance.customer.accounts.all()[0]
    old_blc= account.balance
    account.balance=Decimal(old_blc)-Decimal(instance.cost())
    account.save()
    if account.balance <=0:
        subject="Dear %s your  coffee credit is 0. Pls come to pay some more! Thanks!"%instance.customer.name
        content="Dear %s your  coffee credit is 0. Pls come to pay some more! Thanks!"%instance.customer.name
        EmailAlert.objects.create(content=content,subject=subject,customer=instance.customer)


post_save.connect(check_balance_handler, sender=CoffeeOrder)

class MessageContent(models.Model):
    email_type_choices = (('alert', 'Balance Alert'), ('marketing', 'Marketing'))
    subject = models.TextField()
    sender = models.EmailField(default='no-reply@uganda.rapidsms.org')
    message = models.TextField()
    type = models.CharField(max_length=15, default='alert', choices=email_type_choices, blank=True, null=True)


class Badge(models.Model):
    """Awarded for notable coffee drinking."""
    GOLD = 1
    SILVER = 2
    BRONZE = 3
    TYPE_CHOICES = (
        (GOLD,   u'gold'),
        (SILVER, u'silver'),
        (BRONZE, u'bronze'),
    )

    name        = models.CharField(max_length=50)
    type        = models.SmallIntegerField(choices=TYPE_CHOICES)
    description = models.CharField(max_length=300)
    multiple    = models.BooleanField(default=False)
    # Denormalised data
    awarded_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('name',)
        unique_together = ('name', 'type')

class Award(models.Model):
    """The awarding of a Badge to a Customer."""
    customer       = models.ForeignKey(Customer)
    badge      = models.ForeignKey(Badge)
    awarded_at = models.DateTimeField(default=datetime.now)
    notified   = models.BooleanField(default=False)



class EmailAlert(models.Model):
    subject = models.TextField()
    sender = models.EmailField(default='no-reply@uganda.rapidsms.org')
    content = models.TextField()
    sent=models.BooleanField(default=False)
    customer=models.ForeignKey(Customer,null=True,blank=True)
    date_to_send=models.DateTimeField(default=datetime.now()+timedelta(days=1))

def create_new_account(sender, **kwargs):
    if sender == Customer:
        customer = kwargs['instance']
        if customer:
            if not customer.accounts.exists():
                customer.accounts.create()

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

    name = find_best_response(session, name_poll)
    extension = find_best_response(session, extension_poll)
    department = find_best_response(session, department_poll)
    email = find_best_response(session, email_poll)
    if name:
        name = ' '.join([n.capitalize() for n in name.lower().split()])

    try:
        existing_contact = Customer.objects.get(name=name[:100], \
                                  extension=extension, \
                                  email=email)
        if connection.contact:
            connection.contact.active = True
        else:
            existing_contact.active = True
            existing_contact.save()
            connection.contact = existing_contact
            connection.save()

    except Customer.MultipleObjectsReturned:
        pass

    except Customer.DoesNotExist:

        connection.contact = Customer.objects.create()
        connection.save()
        contact = connection.contact

        if name:
            name = ' '.join([n.capitalize() for n in name.lower().split(' ')])
            contact.name = name[:100]

        if department:
            group = find_closest_match(department, Group.objects)
            if not group:
                group = Group.objects.get(name='Other Coffee People')
        contact.groups.add(group)

        if extension:
            contact.extension = extension

        if email:
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

def xform_received_handler(sender, **kwargs):
    xform = kwargs['xform']
    submission = kwargs['submission']
    contact = Contact.objects.get(pk=kwargs['message'].connection.contact_id)

    if xform.keyword == 'coffee':
        date = datetime.now()
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
post_save.connect(create_new_account, sender=Customer, weak=False)



