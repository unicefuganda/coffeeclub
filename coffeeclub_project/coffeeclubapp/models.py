from django.db import models
try:
    from rapidsms.models import Contact
except:
    Contact=type('Contact',(models.Model,),{'__module__':'coffeeclubapp.models','app_label':'','fields':None})

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
    customer=models.ForeignKey(Contact)
    item=models.ForeignKey(MenuItem)
    count=models.IntegerField(max_length=2)


class Account(models.Model):
    customer=models.ForeignKey(Contact)
    amount=models.IntegerField(max_length=10)




