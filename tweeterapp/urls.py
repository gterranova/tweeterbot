from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    "",
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^login/$', views.HomeView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^feeds/$', views.TweetIndexView.as_view(), name='feeds'),
    url(r'^all-feeds/$', views.AllTweetsIndexView.as_view(), name='all_feeds'),
    url(r'^publish/(?P<pk>[0-9]+)/$', views.TweetPublishView.as_view(), name='publish'),
    url(r'^retweet/(?P<pk>[0-9]+)/$', views.RetweetRedirectView.as_view(), name='retweet'),
    url(r'^delete/(?P<pk>[0-9]+)/$', views.TweetDeleteView.as_view(), name='delete'),

    url(r'^tweet_store/$', views.TweetStoreIndexView.as_view(), name='tweetstore_index'),
    url(r'^tweet_store/create/$', views.TweetStoreCreateView.as_view(), name='tweetstore_add'),
    url(r'^tweet_store/(?P<pk>[0-9]+)/edit$', views.TweetStoreUpdateView.as_view(), name='tweetstore_edit'),
    url(r'^tweet_store/(?P<pk>[0-9]+)/delete$', views.TweetStoreDeleteView.as_view(), name='tweetstore_delete'),
)
