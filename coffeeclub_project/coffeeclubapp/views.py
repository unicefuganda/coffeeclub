from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms import ModelForm
from .models import *
from django import forms
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.validators import validate_email

class OrderForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['customer'].widget.attrs['class'] = 'autocomplete'
        self.fields['customer'].help_text="start typing to see available customers"
        self.fields['coffee_name'].widget.attrs['class'] = 'autocomplete'
        self.fields['coffee_name'].help_text="start typing to see available Menu Items"

    class Meta:
        model=CoffeeOrder

class CustomerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['groups'].widget.attrs['class'] = 'autocomplete'
        self.fields['groups'].label="Group"
        self.fields['groups'].help_text="starty typing to see available groups"
    class Meta:
        model=Customer
        exclude=('language','user','user_permissions','reporting_location','preferences')
    def clean(self):
        cleaned_data = self.cleaned_data
        if self._errors and 'email' in self._errors:
            raise forms.ValidationError("Email already exists")
        else:
            return cleaned_data
    

class PrefrencesForm(ModelForm):
    class Meta:
        model=CustomerPref
def dashboard(request):
    order_form=OrderForm()
    if request.method=='POST':
        order_form=OrderForm(request.POST)
        if order_form.is_valid():
            order_form.save()
    return render_to_response('coffeeclubapp/dashboard.html',{'order_form':order_form},
    context_instance=RequestContext(request))

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
    return render_to_response('coffeeclubapp/customer_detail.html',{'customer':customer},
                              context_instance=RequestContext(request))
