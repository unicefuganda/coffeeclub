from django.conf.urls.defaults import *
from coffeeclubapp.views import dashboard
from rapidsms_httprouter.urls import urlpatterns as router_urls
from django.conf import settings


from generic.urls import urlpatterns as generic_urls

urlpatterns = patterns('',

        url(r'^$', dashboard ,name="coffee-dashboard"),
        (r'^account/', include('rapidsms.urls.login_logout')),
            url('^accounts/login', 'rapidsms.views.login'),
            url('^accounts/logout', 'rapidsms.views.logout'),
            # RapidSMS contrib app URLs
            (r'^ajax/', include('rapidsms.contrib.ajax.urls')),
            (r'^export/', include('rapidsms.contrib.export.urls')),
            (r'^httptester/', include('rapidsms.contrib.httptester.urls')),
            (r'^messagelog/', include('rapidsms.contrib.messagelog.urls')),
            (r'^messaging/', include('rapidsms.contrib.messaging.urls')),
            (r'^registration/', include('auth.urls')),
            (r'^scheduler/', include('rapidsms.contrib.scheduler.urls')),
            (r'^polls/', include('poll.urls')),
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
