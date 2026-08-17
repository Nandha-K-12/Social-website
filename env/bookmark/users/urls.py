from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import path, reverse_lazy
from . import views
app_name = 'users'


urlpatterns = [

    # Login
    path(
        'login/',
        LoginView.as_view(
            template_name='authentication/login.html'
        ),
        name='login'
    ),

    # Logout
    path(
        'logout/',
        LogoutView.as_view(),
        name='logout'
    ),

    # Dashboard
    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    # Change password
    path(
    'password_change/',
    PasswordChangeView.as_view(
        template_name='authentication/password_change_form.html',
        success_url=reverse_lazy(
            'users:password_change_done'
        ),
    ),
    name='password_change'
),

    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name='authentication/password_change_done.html'
        ),
        name='password_change_done'
    ),

    # Password reset
   path(
    'password_reset/',
    PasswordResetView.as_view(
        template_name='authentication/password_reset_form.html',
        email_template_name='authentication/password_reset_email.html',
        subject_template_name='authentication/password_reset_subject.txt',
        success_url=reverse_lazy(
            'users:password_reset_done'
        ),
    ),
    name='password_reset'
),

    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(
            template_name='authentication/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='authentication/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(
            template_name='authentication/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    
    path(
    'edit/',
    views.edit,
    name='edit'),
        # User profiles and follow system
    path('users/', views.user_list, name='user_list'),
    path('users/follow/', views.user_follow, name='user_follow'),
    path('users/<username>/', views.user_detail, name='user_detail'),

]
