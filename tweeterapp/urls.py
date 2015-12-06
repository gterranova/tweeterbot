from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    "",
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^login/$', views.HomeView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^feeds/$', views.TweetIndexView.as_view(), name='feeds'),
    url(r'^retweet/(?P<pk>[0-9]+)/$', views.RetweetRedirectView.as_view(), name='retweet'),
)
