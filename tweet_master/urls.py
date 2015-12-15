try:
    from django.conf.urls import url, patterns
except ImportError:
    from django.conf.urls.defaults import url, patterns
from .views import SlavesList,\
    MastersList, FollowRedirectView, UnfollowRedirectView, FollowerRemoveRedirectView, UsersList

urlpatterns = patterns('',
    url(
        regex=r'^users/$',
        view=UsersList.as_view(),
        name='friendship_view_users',
    ),
    url(
        regex=r'^followers/(?P<username>[\w-]+)/$',
        view=SlavesList.as_view(),
        name='friendship_followers',
    ),
    url(
        regex=r'^following/(?P<username>[\w-]+)/$',
        view=MastersList.as_view(),
        name='friendship_following',
    ),
    url(
        regex=r'^follow/(?P<username>[\w-]+)/$',
        view=FollowRedirectView.as_view(),
        name='master_add',
    ),
    url(
        regex=r'^unfollow/(?P<username>[\w-]+)/$',
        view=UnfollowRedirectView.as_view(),
        name='master_remove',
    ),
    url(
        regex=r'^removefollower/(?P<username>[\w-]+)/$',
        view=FollowerRemoveRedirectView.as_view(),
        name='follower_remove',
    ),
)
