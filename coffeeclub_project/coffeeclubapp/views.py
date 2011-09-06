from django.shortcuts import render_to_response

def dashboard(request):
    var_test = "food"
    return render_to_response('coffeeclubapp/dashboard.html',locals())
