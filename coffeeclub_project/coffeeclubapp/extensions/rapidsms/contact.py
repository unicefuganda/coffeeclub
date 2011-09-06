from django.db import models
from coffeeclubapp.models import CustomerPref


class CoffeeContact(models.Model):
    """
    This extension for Contacts allows developers to tie a Contact to coffeeclub prefs

    """
    preferences = models.ForeignKey(CustomerPref, blank=True, null=True)

    class Meta:
        abstract = True