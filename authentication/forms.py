from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=255)
    email = forms.EmailField(widget=forms.EmailInput)
    password = forms.CharField(max_length=68, min_length=6, widget=forms.PasswordInput)


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput)
    password = forms.CharField(max_length=68, min_length=6, widget=forms.PasswordInput)