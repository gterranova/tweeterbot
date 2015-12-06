# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import tweepy
from random import shuffle

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, login, get_user_model

from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social.apps.django_app.utils import psa

from .decorators import render_to
from django.views import generic
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.contrib import messages

from models import Tweet
from forms import TweetForm

from social.backends.google import GooglePlusAuth
from social.backends.utils import load_backends


class AvailableBackendsMixin(object):
    def get_context_data(self, **kwargs):
        context = super(AvailableBackendsMixin, self).get_context_data(**kwargs)
        return dict({
            'plus_id': getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None),
            'plus_scope': ' '.join(GooglePlusAuth.DEFAULT_SCOPE),
            'available_backends': load_backends(settings.AUTHENTICATION_BACKENDS)
        }, **context)

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)

class AdminRequiredMixin(object):
    def get_object(self, *args, **kwargs):
        obj = super(AdminRequiredMixin, self).get_object(*args, **kwargs)
        if self.request.user.is_staff:
            return obj
        raise PermissionDenied("The user does not have permission to do that.")

class TweepyMixin(object):
    def get_twitter_api(self, user):
        consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY
        consumer_secret = settings.SOCIAL_AUTH_TWITTER_SECRET
        access_token = user.social_auth.first().access_token
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token['oauth_token'], access_token['oauth_token_secret'])
        api = tweepy.API(auth)
        return api
        
class LogoutView(LoginRequiredMixin, generic.RedirectView):
    """Home view, displays login mechanism"""
    permanent = False
    def get(self, request, *args, **kwargs):
        auth_logout(request)
        self.url = reverse_lazy('home')
        return super(LogoutView, self).get(request, args, **kwargs)

class HomeView(AvailableBackendsMixin, TweepyMixin, generic.CreateView):
    """Home view, displays login mechanism"""
    model = Tweet
    template_name = 'home.html'

    def get_form(self):
        form = TweetForm(auto_id=False, **self.get_form_kwargs())
        form.fields['author'].queryset = get_user_model().objects.filter(Q(is_staff=False) | Q(pk=self.request.user.id))
        return form
        
    def get_initial(self):
        initial = super(HomeView, self).get_initial()
        initial['author'] = self.request.user
        return initial
        
    def get_success_url(self):
        return reverse("feeds")
        
    def form_valid(self, form):
        user = form.cleaned_data['author']
        content = form.cleaned_data['content']
        api = self.get_twitter_api(user)
        status = api.update_status(content)

        tweet = Tweet()
        tweet.author = user
        tweet.twitter_id_str = status.id_str
        tweet.published_at = status.created_at
        tweet.content = status.text
        tweet.save()
        
        return HttpResponseRedirect(self.get_success_url())
                    
class TweetIndexView(LoginRequiredMixin, AvailableBackendsMixin, generic.ListView):
    paginate_by = 10
    model = Tweet
    template_name = 'feeds.html'
    context_object_name = 'tweets'
            
    def get_queryset(self):
        update = self.request.GET.get('refresh', 0)
        return Tweet.objects.get_latest_tweets(self.request.user, update=update)

class RetweetRedirectView(LoginRequiredMixin, TweepyMixin, generic.RedirectView):
    permanent = False
    def get(self, request, *args, **kwargs):
        tweet = Tweet.objects.get(pk=self.kwargs['pk'])
        users = get_user_model().objects.filter(is_staff=False).exclude(pk=self.request.user.id)
        users = [u for u in users.all() if u.social_auth.count() != 0 and not u.retwits.filter(id=tweet.id).exists()]
        shuffle(users)
        if users and len(users) > 0:
            api = self.get_twitter_api(users[0])
            response = api.retweet(tweet.twitter_id_str)
            #print response, response.retweet_count
            tweet.retwittered_by.add(users[0])
            tweet.save()
            messages.success(self.request, "Retweet by %s" % users[0])
        else:
            messages.error(self.request, "No more users for retweetting")
            
        self.url = reverse_lazy('feeds')
        return super(RetweetRedirectView, self).get(request, args, **kwargs)
        
@render_to('home.html')
def validation_sent(request):
    return context(
        validation_sent=True,
        email=request.session.get('email_validation_address')
    )


@render_to('home.html')
def require_email(request):
    backend = request.session['partial_pipeline']['backend']
    return context(email_required=True, backend=backend)


@psa('social:complete')
def ajax_auth(request, backend):
    if isinstance(request.backend, BaseOAuth1):
        token = {
            'oauth_token': request.REQUEST.get('access_token'),
            'oauth_token_secret': request.REQUEST.get('access_token_secret'),
        }
    elif isinstance(request.backend, BaseOAuth2):
        token = request.REQUEST.get('access_token')
    else:
        raise HttpResponseBadRequest('Wrong backend type')
    user = request.backend.do_auth(token, ajax=True)
    login(request, user)
    data = {'id': user.id, 'username': user.username}
    return HttpResponse(json.dumps(data), mimetype='application/json')
