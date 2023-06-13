from typing import Any, Mapping, Optional, Type, Union
from django import forms
from django.forms.utils import ErrorList
from .apps import WebadminConfig
from domena.settings import MEDIA_ROOT



class Profile02Form(forms.Form):

    username= forms.CharField(label="User name::",max_length=255,required=True)

    first_name=forms.CharField(label="First name:",max_length=255,required=False)
    last_name=forms.CharField(label="Last name:",max_length=255,required=False)

    email=forms.CharField(label="E-mail:",max_length=255,widget=forms.EmailInput,required=False)

    project=forms.MultipleChoiceField(label="Project",widget=forms.CheckboxSelectMultiple,
        choices=WebadminConfig.get_available_groups,required=False)


class ProfileImage02Form(forms.Form):
    picture=forms.ImageField()
    
    
class Register02Form(forms.Form):

    username= forms.CharField(label="Login:",max_length=255,required=True)
    password= forms.CharField(label="Password:",max_length=255,
                              widget=forms.PasswordInput,required=True)
    confirm_password=forms.CharField(label="Confirm Password:",max_length=255,
                              widget=forms.PasswordInput,required=True)

    first_name=forms.CharField(label="First name:",max_length=255,required=False)
    last_name=forms.CharField(label="Last name:",max_length=255,required=False)

    email=forms.CharField(label="E-mail:",max_length=255,widget=forms.EmailInput,required=False)
    
    project=forms.MultipleChoiceField(label="Project",widget=forms.CheckboxSelectMultiple,
        choices=WebadminConfig.get_available_groups,required=False)
    
    def clean(self):
        cleaned_data = super(Register02Form, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )
    
    