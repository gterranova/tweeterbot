from django.contrib import admin
from models import Tweet, TweetStore
from forms import TweetForm

# Register your models here.
admin.site.register(Tweet)
admin.site.register(TweetStore)

