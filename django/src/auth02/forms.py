from django import forms

from allauth.account.forms import LoginForm,PasswordField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext, gettext_lazy as _, pgettext


class LoginForm02(LoginForm):

    password = PasswordField(label=_("Password"), autocomplete="current-password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        
        self.fields["password"].help_text = mark_safe(f"")