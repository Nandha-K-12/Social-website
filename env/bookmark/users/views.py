from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from common.decorators import ajax_required
from actions.models import Action
from .forms import (
    UserRegistrationForm,
    UserEditForm,
    ProfileEditForm,
)
from .models import Profile, Contact
from actions.utils import create_action


class UserLoginView(LoginView):
    template_name = 'authentication/login.html'


@login_required
def dashboard(request):
    # Display all actions by default
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)
    
    if following_ids:
        # If user is following others, retrieve only their actions
        actions = actions.filter(user_id__in=following_ids)
    
    # QuerySet Optimization:
    # 1. select_related: Performs an SQL JOIN for ForeignKey/OneToOne (user and user.profile)
    # 2. prefetch_related: Pre-fetches generic target objects in a batch
    actions = actions.select_related('user', 'user__profile').prefetch_related('target')[:10]
    return render(
        request,
        'dashboard.html',
        {
            'section': 'dashboard',
            'actions': actions
        }
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
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(
        request,
        'account/edit.html',
        {
            'section': 'dashboard',
            'user_form': user_form,
            'profile_form': profile_form,
        }
    )


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(
        request,
        'users/user/list.html',
        {'section': 'people', 'users': users}
    )


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(
        request,
        'users/user/detail.html',
        {'section': 'people', 'user': user}
    )


@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user
                )
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(
                    user_from=request.user,
                    user_to=user
                ).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
