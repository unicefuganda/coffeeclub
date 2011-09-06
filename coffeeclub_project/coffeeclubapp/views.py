from django.shortcuts import render_to_response

def dashboard(request):
    return render_to_response('coffeeclubapp/dashboard.html')

def cutomer_detail(request):
    return render_to_response('coffeeclubapp/customer_detail.html')
