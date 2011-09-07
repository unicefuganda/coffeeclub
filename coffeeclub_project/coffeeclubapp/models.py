from django.db import models
from django.db.models.signals import class_prepared
from rapidsms.models import Contact
from django.contrib.auth.models import Group
from script.signals import script_progress_was_completed
from script.models import ScriptSession
from script.utils.handling import find_closest_match, find_best_response

class Department(Group):
    floor = models.CharField(max_length=15, blank=True)

class MenuItem(models.Model):
    name = models.CharField(max_length=50, blank=True)
    cost = models.IntegerField(max_length=10, blank=True, null=True)

class CustomerPref(models.Model):
    milk_type_choices = (('Either', 'Either'),)
    running_order = models.BooleanField(default=False, blank=True)
    milk_type = models.CharField(max_length=50, choices=milk_type_choices, blank=True, null=True)
    own_cup = models.BooleanField(default=False, blank=True)
    notes = models.TextField(blank=True, null=True)
    standard_drink = models.ForeignKey(MenuItem, blank=True, null=True)
    days_on_call = models.CharField(max_length=200, blank=True, null=True)

class Customer(Contact):
    preferences = models.ForeignKey(CustomerPref, related_name='preferences', null=True)
    extension = models.CharField(max_length=30,null=True,blank=True)
    email = models.EmailField(blank=True,null=True)

class Order(models.Model):
    date = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(Customer, related_name="order")
    item = models.ForeignKey(MenuItem)
    count = models.IntegerField(max_length=2,default=1)


class Account(models.Model):
    owner = models.ForeignKey(Customer, related_name="account")
    balance = models.IntegerField(max_length=10,blank=True,null=True)
    date_updated = models.DateTimeField(auto_now=True)


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
            connection.save
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

    prefs = CustomerPref.objects.create()
    drink = find_best_response(session, coffee_standard_poll)
    if drink:
        prefs.standard_drink = find_closest_match(drink, MenuItem.objects)

    milktype = find_best_response(session, milktype_poll)
    if milktype:
        milktype = ' '.join([n.capitalize() for n in milktype.lower().split(' ')])
        prefs.milk_type = milktype


    prefs.save()
    contact.preferences = prefs
    contact.save()

#
#
#
#
#
#    subcounty = find_best_response(session, subcounty_poll)
#    district = find_best_response(session, district_poll)
#
#    if subcounty:
#        subcounty = find_closest_match(subcounty, Location.objects.filter(type__name='sub_county'))
#
#    if subcounty:
#        contact.reporting_location = subcounty
#    elif district:
#        contact.reporting_location = district
#    else:
#        contact.reporting_location = Location.tree.root_nodes()[0]
#
#    name = find_best_response(session, name_poll)
#    if name:
#        name = ' '.join([n.capitalize() for n in name.lower().split(' ')])
#        contact.name = name[:100]
#
#    if not contact.name:
#        contact.name = 'Anonymous User'
#    contact.save()
#
#    reporting_school = None
#    school = find_best_response(session, school_poll)
#    if school:
#        if subcounty:
#            reporting_school = find_closest_match(school, School.objects.filter(location__name__in=[subcounty], \
#                                                                                location__type__name='sub_county'), True)
#        elif district:
#            reporting_school = find_closest_match(school, School.objects.filter(location__name__in=[district.name], \
#                                                                            location__type__name='district'), True)
#        else:
#            reporting_school = find_closest_match(school, School.objects.filter(location__name=Location.tree.root_nodes()[0].name))
#        contact.school = reporting_school
#        contact.save()

#add preferencies to the contact class
#def alter_contacts(sender, **kwargs):
#    if sender.__module__ == 'rapidsms.models' and sender.__name__ == 'Contact':
#        preferences = models.ForeignKey(CustomerPref, blank=True, null=True)
#        order.contribute_to_class(sender, 'order')
#
#class_prepared.connect(alter_contacts)


script_progress_was_completed.connect(coffee_autoreg, weak=False)



