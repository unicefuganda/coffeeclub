'''
Created on Sep 8, 2011

@author: asseym
'''
from coffeeclubapp.models import Customer, Account
from django.template import loader, Context, Template
from django.core.mail import send_mass_mail


def balance_alerts(bal=False, subj=False, signature=False):
    customers = Customer.objects.filter(active=True)
    for customer in customers:
        if customer.accounts.all()[0].balance < 0:
            bal = bal if bal else Account.objects.filter(customer=customer)[0].balance
            subj = subj if subj else 'Outstanding Balance Alert'
            signature = signature if signature else 'Management'
            ctxt = {'customer':customer, 'subject':subj, 'bal':bal, 'signature':signature}
            customer.send_email(ctxt)

def marketing_email(subject=False, message=False):
    customers = Customer.objects.filter(active=True)
    for customer in customers:
        subject = subject if subject else 'Buy 1 get 4 free!'
        message = message if message else 'This September buy 1 expresso and get 4 on the house!'
        ctxt = {'customer':customer, 'subject':subject, 'marketing_message':message}
        customer.send_email(ctxt, type='marketing')

def send_template_email(recipients, template,sender, context,subject):
    t = loader.get_template(template)
    context.update(dict(content=content))
    t.render(Context(context))
    send_mass_mail(subject, t, sender, recipients)
