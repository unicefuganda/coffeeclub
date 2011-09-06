from django.db import models
from django.db.models.signals import class_prepared
from rapidsms.models import Contact


class MenuItem(models.Model):
    name=models.CharField(max_length=50,blank=True)
    cost=models.IntegerField(max_length=10,blank=True,null=True)

class CustomerPref(models.Model):
    milk_type_choices=(('Either','Either'),)
    running_order=models.BooleanField(default=False)
    extension=models.CharField(max_length=30)
    milk_type=models.CharField(max_length=50,choices=milk_type_choices)
    own_cup=models.BooleanField(default=False)
    notes=models.TextField()
    standard_drink=models.ForeignKey(MenuItem)
    days_on_call=models.CharField(max_length=200)
    email=models.EmailField()


class Order(models.Model):
    date=models.DateTimeField()
    customer=models.ForeignKey(Contact,related_name="order")
    item=models.ForeignKey(MenuItem)
    count=models.IntegerField(max_length=2)


class Account(models.Model):
    owner=models.ForeignKey(Contact,related_name="account")
    balance=models.IntegerField(max_length=10)
    date_updated=models.DateTimeField(auto_now=True)

#add preferencies to the contact class
def alter_contacts(sender, **kwargs):
    if sender.__module__ == 'rapidsms.models' and sender.__name__ == 'Contact':
        preferences = models.ForeignKey(CustomerPref, blank=True, null=True)
        order.contribute_to_class(sender, 'order')

class_prepared.connect(alter_contacts)






