from django.views.generic import CreateView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .models import CustomUser, Profile
from .forms import CustomUserCreationForm, ProfileForm


class CustomLoginView(LoginView):
    template_name = 'user/login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        if not user.is_account_confirmed and not user.is_superuser:
            messages.error(
                self.request,
                'Your account is pending approval from the manager.'
            )
            return self.form_invalid(form)
        return super().form_valid(form)


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'user/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Your account has been created and is pending approval from the manager.'
        )
        print(form.cleaned_data)

        return response


class PendingUserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'user/pending_users.html'
    context_object_name = 'pending_users'

    def test_func(self):
        return self.request.user.user_type == 'manager'

    def get_queryset(self):
        return CustomUser.objects.filter(is_account_confirmed=False)\
            .exclude(is_superuser=True)


class ConfirmUserView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CustomUser
    fields = ['is_account_confirmed']
    template_name = 'user/confirm_user.html'
    success_url = reverse_lazy('pending-users')

    def test_func(self):
        # Restrict access to managers only
        return self.request.user.user_type == 'manager'

    def form_valid(self, form):
        # Automatically set is_account_confirmed to True
        form.instance.is_account_confirmed = True
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Account for {self.object.username} has been confirmed."
        )
        return response


class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'user/dashboard.html'
    context_object_name = 'dashboard_data'

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'manager':
            return {
                'projects': user.managed_projects.all(),
                'pending_users': CustomUser.objects.filter(
                    is_account_confirmed=False).exclude(is_superuser=True)
            }
        elif user.user_type == 'team_member':
            return {
                'tasks': user.assigned_tasks.all()
            }
        else:  # client
            return {
                'projects': user.client_projects.all()
            }
