from django.conf.urls.defaults import *
from coffeeclubapp.views import dashboard
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
      (r'^$', dashboard),
)