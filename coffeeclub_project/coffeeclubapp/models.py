from django.db import models

class MenuItem(models.Model):
    name=models.CharField(max_length=50,blank=True)
    cost=models.IntegerField(max_length=10,blank=True,null=True)

class Customer(models.Model):
    #user=models.ForeignKey(Contact,related_name="customer")
    running_order=models.BooleanField(default=False)

class Order(models.Model):
    customer=models.ForeignKey(Customer)

class Account(models.Model):
    pass