from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
class UserLoginView(LoginView):
    template_name = 'authentication/login.html'

@login_required
def dashboard(request):
    return render(
        request,
        'dashboard.html'
    )