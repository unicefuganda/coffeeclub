from django.shortcuts import render_to_response
from django.template import RequestContext

def dashboard(request):

    return render_to_response('coffeeclubapp/dashboard.html',context_instance=RequestContext(request))

def cutomer_detail(request):
    return render_to_response('coffeeclubapp/customer_detail.html',context_instance=RequestContext(request))

