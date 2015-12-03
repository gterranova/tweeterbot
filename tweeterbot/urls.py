"""tweeterbot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^email-sent/', 'tweeterapp.views.validation_sent'),
    url(r'^login/$', 'tweeterapp.views.home'),
    url(r'^logout/$', 'tweeterapp.views.logout'),
    url(r'^done/$', 'tweeterapp.views.done', name='done'),
    url(r'^ajax-auth/(?P<backend>[^/]+)/$', 'tweeterapp.views.ajax_auth',
        name='ajax-auth'),
    url(r'^email/$', 'tweeterapp.views.require_email', name='require_email'),
    url(r'', include('social.apps.django_app.urls', namespace='social'))    
]
