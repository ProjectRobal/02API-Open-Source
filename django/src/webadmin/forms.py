from django import forms
from .apps import WebadminConfig



class LoginForm(forms.Form):

    user= forms.CharField(label="Login:",max_length=255,required=True)
    pwd= forms.CharField(label="Password:",max_length=255,
                              widget=forms.PasswordInput,required=True)
    

GROUPS_SELECT= [
    ("blue", "Blue"),
    ("green", "Green"),
    ("black", "Black"),
]

    
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
        choices=WebadminConfig.AVAILABLE_GROUPS,required=False)
    
    def clean(self):
        cleaned_data = super(Register02Form, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )
    
    