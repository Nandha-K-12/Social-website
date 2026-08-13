from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Profile

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user = authenticate(
                username=username,
                password=password
            )

            if self.user is None:
                raise forms.ValidationError(
                    'Invalid username or password.'
                )

            if not self.user.is_active:
                raise forms.ValidationError(
                    'This account is disabled.'
                )

        return cleaned_data

class UserRegistrationForm(forms.ModelForm):

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'email',
        )

    def clean_password2(self):
        cd = self.cleaned_data

        if cd['password'] != cd['password2']:
            raise forms.ValidationError(
                "Passwords don't match."
            )

        return cd['password2']

        
class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = (
            'date_of_birth',
            'photo',
        )