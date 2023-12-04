import hashlib
import urllib
from django import template
from django.utils.safestring import mark_safe
from auth02.models import O2User
from ..models import ProfilePicture
from domena.settings import MEDIA_URL

register = template.Library()
 
# return only the URL of the gravatar
# TEMPLATE USE:  {{ email|gravatar_url:150 }}
@register.filter
def gravatar_url(user:O2User, size=40):
  try:
    default = ProfilePicture.objects.get(user=user)
    return '{0}/{1}'.format(MEDIA_URL,default.image)
  except ProfilePicture.DoesNotExist:
    return "https://www.gravatar.com/avatar/%s?%s" % (hashlib.md5(user.email.lower().encode()).hexdigest(),"/static/dummy.png")
 
# return an image tag with the gravatar
# TEMPLATE USE:  {{ email|gravatar:150 }}
@register.filter
def gravatar(user:O2User, size=40):
    url = gravatar_url(user.email, size)
    return mark_safe('<img src="%s" width="%d" height="%d">' % (url, size, size))