from django.shortcuts import render_to_response

def dashboard(request):

    return render_to_response('coffeeclubapp/dashboard.html')

