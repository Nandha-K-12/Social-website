from django import forms
from django.contrib.auth import authenticate


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