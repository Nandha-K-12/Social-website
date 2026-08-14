# pyrefly: ignore [missing-import]
from django.shortcuts import render
# pyrefly: ignore [missing-import]
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .forms import (
    UserRegistrationForm,
    UserEditForm,
    ProfileEditForm,
)
from .models import Profile
from django.contrib import messages
class UserLoginView(LoginView):
    template_name = 'authentication/login.html'

@login_required
def dashboard(request):
    return render(
        request,
        'dashboard.html',
        {'section': 'dashboard'}
    )
@login_required
def edit(request):

    if request.method == 'POST':

        user_form = UserEditForm(
            instance=request.user,
            data=request.POST
        )

        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES
        )

        if user_form.is_valid() and profile_form.is_valid():

            user_form.save()
            profile_form.save()

            messages.success(
                request,
                'Profile updated successfully'
            )

        else:

            messages.error(
                request,
                'Error updating your profile'
            )

    else:

        user_form = UserEditForm(
            instance=request.user
        )

        profile_form = ProfileEditForm(
            instance=request.user.profile
        )

    return render(
        request,
        'account/edit.html',
        {
            'section': 'dashboard',
            'user_form': user_form,
            'profile_form': profile_form,
        }
    )