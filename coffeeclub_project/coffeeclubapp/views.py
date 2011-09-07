from django.shortcuts import render_to_response
from django.template import RequestContext
from django.forms import ModelForm
from .models import *
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
    if request.method=='POST':
        order_form=OrderForm(request.POST)
        if order_form.is_valid():
            order_form.save()
    return render_to_response('coffeeclubapp/dashboard.html',{'order_form':order_form},
    context_instance=RequestContext(request))

def edit_customer(request):
    pass
def cutomer_detail(request):
    return render_to_response('coffeeclubapp/customer_detail.html',context_instance=RequestContext(request))
