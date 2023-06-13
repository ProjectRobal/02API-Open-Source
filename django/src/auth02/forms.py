from django import forms


class LoginForm(forms.Form):

    user= forms.CharField(label="Login:",max_length=255,required=True)
    pwd= forms.CharField(label="Password:",max_length=255,
                              widget=forms.PasswordInput,required=True)
