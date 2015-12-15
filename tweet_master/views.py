from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.urlresolvers import reverse_lazy, reverse

try:
    from django.contrib.auth import get_user_model
    user_model = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
    user_model = User

from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib import messages

from tweet_master.exceptions import AlreadyExistsError
from tweet_master.models import TweetMasterRelationship


from tweeterapp.views import AvailableBackendsMixin, LoginRequiredMixin


class SlavesList(AvailableBackendsMixin, generic.TemplateView):
    template_name='tweet_master/slaves_list.html'
    
    def get_context_data(self, **kwargs):
        context = super(SlavesList, self).get_context_data(**kwargs)
        user = get_object_or_404(user_model, username=kwargs.get('username', None))
        
        return dict({
            'master': user,
            'slaves': TweetMasterRelationship.objects.slaves(user),
        }, **context)
    
class MastersList(AvailableBackendsMixin, generic.TemplateView):
    template_name='tweet_master/masters_list.html'
    
    def get_context_data(self, **kwargs):
        context = super(MastersList, self).get_context_data(**kwargs)
        user = get_object_or_404(user_model, username=kwargs.get('username', None))
        
        return dict({
            'slave': user,
            'masters': TweetMasterRelationship.objects.masters(user),
        }, **context)

class UsersList(AvailableBackendsMixin, generic.ListView):
    model = user_model
    template_name='tweet_master/users_list.html'
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super(UsersList, self).get_context_data(**kwargs)        
        return dict({
            'following': TweetMasterRelationship.objects.masters(self.request.user),
            'followers': TweetMasterRelationship.objects.slaves(self.request.user),
        }, **context)
    
class FollowRedirectView(AvailableBackendsMixin, LoginRequiredMixin, generic.RedirectView):
    permanent = False
    def get(self, request, *args, **kwargs):
        master = get_object_or_404(user_model, username=kwargs.get('username', None))
        slave = self.request.user
        try:
            TweetMasterRelationship.objects.add_slave(slave, master)
        except AlreadyExistsError as e:
            messages.error(self.request, "%s" % e)
        
        self.url = reverse_lazy('friendship_view_users')
        return super(FollowRedirectView, self).get(request, args, **kwargs)


class UnfollowRedirectView(AvailableBackendsMixin, LoginRequiredMixin, generic.RedirectView):
    permanent = False
    def get(self, request, *args, **kwargs):
        master = get_object_or_404(user_model, username=kwargs.get('username', None))
        slave = self.request.user
        try:
            TweetMasterRelationship.objects.remove_slave(slave, master)
        except AlreadyExistsError as e:
            messages.error(self.request, "%s" % e)
        
        self.url = reverse_lazy('friendship_view_users')
        return super(UnfollowRedirectView, self).get(request, args, **kwargs)

class FollowerRemoveRedirectView(AvailableBackendsMixin, LoginRequiredMixin, generic.RedirectView):
    permanent = False
    def get(self, request, *args, **kwargs):
        master = self.request.user
        slave = get_object_or_404(user_model, username=kwargs.get('username', None))
        try:
            TweetMasterRelationship.objects.remove_slave(slave, master)
        except AlreadyExistsError as e:
            messages.error(self.request, "%s" % e)
        
        self.url = reverse_lazy('friendship_view_users')
        return super(FollowerRemoveRedirectView, self).get(request, args, **kwargs)
        