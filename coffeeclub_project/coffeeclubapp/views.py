from django.shortcuts import render_to_response
from django.template import RequestContext
from .models import *
from .forms import *
from uganda_common.utils import ExcelResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
import datetime
from decimal import Decimal
from .utils import handle_excel_file


def dashboard(request):
    order_form=OrderForm()
    orders=CoffeeOrder.objects.order_by('-date')[:10]
    if request.method=='POST':
        order_form=OrderForm(request.POST)
        if order_form.is_valid():
            order_form.save()
    return render_to_response('coffeeclubapp/dashboard.html',{'order_form':order_form,'orders':orders},
    context_instance=RequestContext(request))


def edit_customer(request,customer_pk=None):
    if customer_pk :
        customer=get_object_or_404(Customer,pk=customer_pk)
        customer_form=CustomerForm(instance=customer)
        preferences_form=PrefrencesForm(instance=customer.preferences)

    elif request.method=='POST':
        customer_form=CustomerForm(request.POST,instance=Customer())
        preferences_form=PrefrencesForm(request.POST,instance=CustomerPref())
        if customer_form.is_valid() and preferences_form.is_valid():
            preferences=preferences_form.save()
            customer_form.cleaned_data['preferences']=preferences
            customer=customer_form.save()
            if customer:
                return HttpResponseRedirect("/")


    else:
        customer_form=CustomerForm()
        preferences_form=PrefrencesForm()

    return render_to_response('coffeeclubapp/edit_customer.html',{'customer_form':customer_form,
                                                                  'preferences_form':preferences_form},
    context_instance=RequestContext(request))

def delete_customer(request,customer_id):
    customer=get_object_or_404(Customer,pk=customer_id)
    if customer:
        customer.delete()
        return HttpResponse("Success")
    else:
        return HttpResponse("Failed")

def customer_details(request,customer_pk):
    customer=get_object_or_404(Customer,pk=customer_pk)
    customer_coffee_order = CoffeeOrder.objects.filter(customer__name__exact=customer.name)

    return render_to_response('coffeeclubapp/customer_detail.html',{'customer':customer,
                                                                    'coffee_order':customer_coffee_order},
                              context_instance=RequestContext(request))

def upload_customers(request):
     if request.method == 'POST':
        upload_form = UploadForm(request.POST, request.FILES)
        if upload_form.is_valid() and request.FILES.get('excel_file',None):
            message= handle_excel_file(request.FILES['excel_file'])
     else:
         upload_form = UploadForm()
     return render_to_response('coffeeclubapp/upload.html',{'upload_form':upload_form},
                              context_instance=RequestContext(request))

def export_cusomers(request):
    customers=Customer.objects.all()
    export_list=[]

    for customer in customers:
        cus={}
        cus['name']=customer.name
        cus['extension']=customer.extension
        cus['email']=customer.email
        if customer.groups.exists():
            cus['location']=customer.groups.all()[0].name
        else:
            cus['location']="N/A"
        if customer.preferences.standard_drink:
            cus['standard_drink']=customer.preferences.standard_drink.name
        else:
            cus['standard_drink']="N/A"
        cus['milk_type']=customer.preferences.milk_type
        cus['running_order']=customer.preferences.running_order
        cus['days_on_call']=customer.preferences.days_on_call
        cus['own_cup']=customer.preferences.own_cup
        cus['notes']=customer.preferences.notes
        cus['balance']=customer.account_bal()
        export_list.append(cus)
    return ExcelResponse(export_list)

def scheduled_emails(request):
    emails=EmailAlert.objects.filter(sent=False)
    return render_to_response('coffeeclubapp/emails.html',dict(emails=emails),
                              context_instance=RequestContext(request))

def delete_email(request,email_pk):
    email=get_object_or_404(EmailAlert,pk=email_pk)
    if email:
        email.delete()

    return HttpResponseRedirect("/customers/emails/")

def edit_email(request,email_pk):
    if email_pk :
        email=get_object_or_404(EmailAlert,pk=email_pk)
        email_form=EmailForm(instance=email)

    elif request.method=='POST':
        email_form=EmailForm(request.POST,instance=EmailAlert())
        if email_form.is_valid():
            email=email_form.save()
            if email:
                return HttpResponseRedirect("/")


    else:
        email_form=EmailForm()


    return render_to_response('coffeeclubapp/edit_email.html',{'email_form':email_form},
                    context_instance=RequestContext(request))



def leaderboard(request):
    leaders=Award.objects.all()
    return render_to_response("coffeeclubapp/leaderboard.html",dict(leaders=leaders),
                              context_instance=RequestContext(request))

# management
def management(request):
    menu_item_form = MenuItemForm()
    return render_to_response('coffeeclubapp/management.html',{'menu_item_form':menu_item_form},context_instance=RequestContext(request))

