from django.contrib.sites.models import Site
from social.backends.google import GooglePlusAuth
from social.backends.utils import load_backends
from django.conf import settings


def theme(request):
    ctx = {
        "THEME_ACCOUNT_BOOTSTRAP_THEME": getattr(settings, 'THEME_ACCOUNT_BOOTSTRAP_THEME', 'readable'),
    }
    if Site._meta.installed:
        site = Site.objects.get_current()
        ctx.update({
            "SITE_NAME": site.name,
            "SITE_DOMAIN": site.domain
        })

    return ctx
    
def available_backends(request):
    return {
        'plus_id': getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None),
        'plus_scope': ' '.join(GooglePlusAuth.DEFAULT_SCOPE),
        'available_backends': load_backends(settings.AUTHENTICATION_BACKENDS)
    }
