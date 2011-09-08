from django.conf.urls.defaults import *
from coffeeclubapp.views import *
from rapidsms_httprouter.urls import urlpatterns as router_urls
from django.conf import settings
from generic.views import generic, generic_row
from generic.sorters import SimpleSorter
from coffeeclubapp.models import Customer

from django.contrib import admin
admin.autodiscover()

from generic.urls import urlpatterns as generic_urls

urlpatterns = patterns('',

        url(r'^$', dashboard ,name="coffee-dashboard"),
        url(r'^account/', include('rapidsms.urls.login_logout')),
        url('^accounts/login', 'rapidsms.views.login'),
        url('^accounts/logout', 'rapidsms.views.logout'),

        url(r'^admin/',include(admin.site.urls)),
        
        # RapidSMS contrib app URLs
        (r'^ajax/', include('rapidsms.contrib.ajax.urls')),
        (r'^export/', include('rapidsms.contrib.export.urls')),
        (r'^httptester/', include('rapidsms.contrib.httptester.urls')),
        (r'^messagelog/', include('rapidsms.contrib.messagelog.urls')),
        (r'^messaging/', include('rapidsms.contrib.messaging.urls')),
        (r'^registration/', include('auth.urls')),
        (r'^scheduler/', include('rapidsms.contrib.scheduler.urls')),

        url(r'^management/',management,name="management_dashboard"),
        (r'^polls/', include('poll.urls')),
        url(r'^customers/(?P<customer_pk>\d+)/edit/',edit_customer,name="edit_customer"),
        url(r'^customers/(?P<customer_pk>\d+)/delete/',delete_customer,name="delete_customer"),
         url(r'^customers/(?P<customer_pk>\d+)/view/',customer_details,name="view_customer"),
        url(r'^customers/new/',edit_customer,name="new_customer"),
        url(r'^customers/upload/',upload_customers,name="upload_customers"),
        url(r'^customers/export/',export_cusomers,name="export_customers"),
        url(r'^customers/$', generic, {
        'model':Customer,
        'queryset':Customer.objects.all(),
        'results_title':'All Customers',
        'filter_forms':[],
        'action_forms':[],
        'objects_per_page':10,
        'partial_row':'coffeeclubapp/partials/customer_row.html',
        'partial_header':'coffeeclubapp/partials/partial_header_dashboard.html',
        'base_template':'coffeeclubapp/customers.html',
        'selectable':False,
        'columns':[('Name', True, 'name', SimpleSorter()),
                 ('Extension', True, 'extension', SimpleSorter(),),
                 ('Location', True, 'start_date', SimpleSorter(),),
                 ('# Standard Drink', False, 'participants', None,),
                 ('Milk Type', False, '', None,),
                 ('Running Order', False, '', None,),
                 ('Days/Week', False, '', None,),
                 ('Own Cup', False, '', None,),
                 ('Notes', False, '', None,),
                 ('Balance', False, '',  SimpleSorter(),),
                 ],
    }, name="poll_dashboard"),
        ) + router_urls  + generic_urls 


if settings.DEBUG:
    urlpatterns += patterns('',
        # helper URLs file that automatically serves the 'static' folder in
        # INSTALLED_APPS via the Django static media server (NOT for use in
        # production)
        (r'^', include('rapidsms.urls.static_media')),
    )

from rapidsms_httprouter.router import get_router
get_router()
