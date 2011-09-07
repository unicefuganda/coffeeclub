from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms import ModelForm
from coffeeclubapp.models import *
from django import forms

class OrderForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['customer'].widget.attrs['class'] = 'autocomplete'
        self.fields['item'].widget.attrs['class'] = 'autocomplete'

    class Meta:
        model=Order
def dashboard(request):
    order_form=OrderForm()
    customers=Customer.objects.order_by('-name')
    return render_to_response('coffeeclubapp/dashboard.html',{'order_form':order_form,'customers':customers},
    context_instance=RequestContext(request))

def cutomer_detail(request):
    return render_to_response('coffeeclubapp/customer_detail.html',context_instance=RequestContext(request))

