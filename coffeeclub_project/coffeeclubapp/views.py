from django.shortcuts import render_to_response
from django.template import RequestContext
from .models import *
from uganda_common.utils import ExcelResponse
from xlrd import open_workbook
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from forms import CustomerForm, OrderForm, PrefrencesForm

def dashboard(request):
    order_form=OrderForm()
    if request.method=='POST':
        order_form=OrderForm(request.POST)
        if order_form.is_valid():
            order_form.save()
    return render_to_response('coffeeclubapp/dashboard.html',{'order_form':order_form},
    context_instance=RequestContext(request))

def handle_excel_file(file):
    if file:
        excel = file.read()
        workbook = open_workbook(file_contents=excel)
        worksheet = workbook.sheet_by_index(0)
        worksheet_count=workbook._all_sheets_count
        for worksheet_index in range(worksheet_count):
            worksheet=workbook.sheet_by_index(worksheet_index)
            extension=worksheet(4,0).value
            name=worksheet(4,1).value
            location=worksheet(4,2).value
            standard_drink=worksheet(4,3).value
            milk_type=worksheet(4,4).value
            running_order=worksheet(4,5).value
            days_on_call=worksheet(4,6).value
            own_cup=worksheet(4,7).value
            notes=worksheet(4,8).value
            email=worksheet(6,1).value
            #create customer

            customer=Customer.objects.create(name=name,extension=extension)
            dep_list=str(location).split(',')
            floor=""
            if(len(dep_list)==2):
                floor=dep_list[1]
            customer.group,created=Department.objects.get_or_create(name=dep_list[0],floor=floor)
            customer.group.save()
            if str(running_order).lower()=='no':
                customer.preferences.running_order=False
            else:
                customer.preferences.running_order=True
            customer.preferences.standard_drink=standard_drink
            customer.preferences.days_on_call=days_on_call

            if str(own_cup).lower()=='no':
                customer.preferences.own_cup=False
            else:
                customer.preferences.own_cup=True

            customer.preferences.milk_type,created=MenuItem.objects.get_or_create(name=milk_type,cost=2500)
            customer.email=email
            customer.email=email
            customer.preferences.save()
            customer.save()
            for row in range(8,worksheet.nrows):
                date_of_payement=datetime.datetime.strptime(worksheet.cell(row,1),"'%d/%m/%Y")

                Account.objects.create()
            



def edit_customer(request,customer_id=None):
    if customer_id :
        customer=get_object_or_404(Customer,pk=customer_id)
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
    return ExcelResponse(customers)
