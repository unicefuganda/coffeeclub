"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""


#from django.utils import unittest

from django.test import TestCase
from coffeeclubapp.models import MenuItem

class MenuItemTestCase(TestCase):
    def setUp(self):
        self.menu_item = MenuItem.objects.create(name="capuccino", cost=2500)
    def testOrder(self):
        self.assertEqual(self.menu_item.set)


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

