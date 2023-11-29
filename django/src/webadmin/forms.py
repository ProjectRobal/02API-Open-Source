from django import forms
from django.forms.utils import ErrorList
from .apps import WebadminConfig
from domena.settings import MEDIA_ROOT
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator 

from common.regexs import login_regex,html_regex

from . import utils


class Profile02Form(forms.Form):

    project=forms.MultipleChoiceField(label="Project",widget=forms.CheckboxSelectMultiple,
        choices=WebadminConfig.get_available_groups,required=False)


class ProfileImage02Form(forms.Form):
    picture=forms.ImageField()