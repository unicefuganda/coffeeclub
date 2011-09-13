'''
Created on Sep 8, 2011

@author: asseym
'''
from coffeeclubapp.models import Customer, Account
from django.template import loader, Context, Template
from django.core.mail import send_mass_mail
from xlrd import open_workbook
from .models import *
import datetime


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

def handle_excel_file(file):
    if file:
        excel = file.read()
        workbook = open_workbook(file_contents=excel)
        worksheet_count=workbook._all_sheets_count
        for worksheet_index in range(worksheet_count):
            worksheet=workbook.sheet_by_index(worksheet_index)
            #parse members
            if worksheet.nrows and str(worksheet.cell(0,0).value).strip()=="Customer Profile Form":
                try:
                    extension=worksheet.cell(4,0).value
                    name=worksheet.cell(4,1).value
                    if name==u"":
                        continue
                    location=worksheet.cell(4,2).value
                    standard_drink=worksheet.cell(4,3).value
                    milk_type=worksheet.cell(4,4).value
                    running_order=worksheet.cell(4,5).value
                    days_on_call=worksheet.cell(4,6).value
                    own_cup=worksheet.cell(4,7).value
                    notes=worksheet.cell(4,8).value
                    email=worksheet.cell(6,1).value
                except IndexError:
                    continue
                #create customer

                customer=Customer.objects.create(name=name,extension=extension)
                dep_list=str(location).split(',')
                floor=""
                dep=str(dep_list[0]).strip()
                if(len(dep_list)==2):
                    floor=dep_list[1][:15]
                if not dep == "":
                    group,created=Department.objects.get_or_create(name=dep[:15])
                    group.floor=floor
                    customer.groups.add(group)
                if str(running_order).strip().lower()=='no':
                    customer.preferences.running_order=False
                else:
                    customer.preferences.running_order=True
                customer.preferences.standard_drink,created=MenuItem.objects.get_or_create(name=str(standard_drink).lower())
                customer.preferences.days_on_call=days_on_call

                if str(own_cup).lower()=='no':
                    customer.preferences.own_cup=False
                else:
                    customer.preferences.own_cup=True
                milk_types=dict(CustomerPref.milk_type_choices)


                customer.preferences.milk_type=milk_types.get(str(milk_type).strip().lower(),'')
                customer.email=email
                customer.preferences.notes=notes
                customer.preferences.save()
                customer.save()
                for row in range(8,worksheet.nrows):
                    try:
                        account,created=Account.objects.get_or_create(customer=customer)
                        old_blc=account.balance
                        b=float(str(worksheet.cell(row,2).value).replace(',','').strip())+float(str(old_blc))
                        account.balance=Decimal(str(b))
                        account.save()
                    except ValueError:
                        continue
                    for v in range(3,7):
                        date=worksheet.cell(row,v).value
                        print date
                        if not date==u"" :
                            try:
                                date_st=datetime.datetime.strptime(str(date)+"/11","%d/%m/%y")
                                order=CoffeeOrder.objects.create(date=date_st,customer=customer,num_cups=1)

                            except ValueError :
                                continue
                        else:
                            continue



            else:
                continue
