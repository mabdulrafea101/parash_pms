from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Project, Milestone, Task, TaskNotification, Payment
from .forms import ProjectForm, MilestoneForm, TaskForm, TaskStatusUpdateForm, PaymentForm
from user.mixins import ManagerRequiredMixin, TeamMemberRequiredMixin, ClientRequiredMixin


# Project Views
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'pms/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'manager':
            return Project.objects.filter(manager=user)
        elif user.user_type == 'client':
            return Project.objects.filter(client=user)
        else:  # team member
            return Project.objects.filter(
                milestones__tasks__assigned_to=user
            ).distinct()


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'pms/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['milestone_form'] = MilestoneForm()
        context['task_form'] = TaskForm()
        
        return context


class ProjectCreateView(LoginRequiredMixin, ManagerRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'pms/project_form.html'
    success_url = reverse_lazy('project-list')

    def form_valid(self, form):
        form.instance.manager = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['manager'] = self.request.user
        return kwargs


class ProjectUpdateView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'pms/project_form.html'
    success_url = reverse_lazy('project-list')

    def get_queryset(self):
        return Project.objects.filter(manager=self.request.user)


# Milestone Views
class MilestoneCreateView(LoginRequiredMixin, ManagerRequiredMixin, CreateView):
    model = Milestone
    form_class = MilestoneForm
    template_name = 'pms/milestone_form.html'

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        form.instance.project = project
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('project-detail',
                            kwargs={'pk': self.kwargs['project_pk']})


class MilestoneDetailView(LoginRequiredMixin, DetailView):
    model = Milestone
    template_name = 'pms/milestone_detail.html'
    context_object_name = 'milestone'


class MilestoneUpdateView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = Milestone
    form_class = MilestoneForm
    template_name = 'pms/milestone_form.html'

    def get_success_url(self):
        return reverse_lazy('project-detail',
                            kwargs={'pk': self.object.project.pk})


class MilestoneDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = Milestone
    template_name = 'pms/milestone_confirm_delete.html'

    def get_queryset(self):
        return Milestone.objects.filter(project__manager=self.request.user)

    def get_success_url(self):
        return reverse_lazy('project-detail',
                            kwargs={'pk': self.object.project.pk})


# Task Views
class TaskCreateView(LoginRequiredMixin, ManagerRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'pms/task_form.html'

    def form_valid(self, form):
        milestone = get_object_or_404(Milestone,
                                      pk=self.kwargs['milestone_pk'])
        form.instance.milestone = milestone
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('project-detail', kwargs={
            'pk': self.object.milestone.project.pk})
    

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'pms/task_detail.html'
    context_object_name = 'task'


class TaskDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = Task
    template_name = 'pms/task_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('project-detail', kwargs={
            'pk': self.object.milestone.project.pk})

    def test_func(self):
        return self.request.user.user_type == 'manager'


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'pms/task_update_form.html'

    def get_form_class(self):
        user = self.request.user
        if user.user_type == 'manager':
            return TaskForm
        else:
            return TaskStatusUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.user_type == 'team_member':
            kwargs['user_type'] = 'team_member'
        elif self.request.user.user_type == 'manager':
            kwargs['user_type'] = 'manager'
        return kwargs

    def form_valid(self, form):
        task = form.instance
        user = self.request.user

        if user.user_type == 'team_member':
            print(form.cleaned_data['status'])
            if form.cleaned_data['status'] == 'not_started':
                task.start_date = None
                task.completed_at = None
                task.save()
            elif form.cleaned_data['status'] == 'started':
                task.start_date = timezone.now()
                task.save()
            
            elif form.cleaned_data['status'] == 'completed':
                task.completed_at = timezone.now()
                task.save()
                # Create notification for manager
                TaskNotification.objects.create(
                    task=task,
                    message=f"Task '{task.title}' has been marked as completed by {user.username}"
                )
        elif user.user_type == 'manager':
            if form.cleaned_data['status'] == 'finalized':
                task.approve_task()
            elif form.cleaned_data['status'] == 'rejected':
                task.reject_task()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('task-detail',
                            kwargs={'pk': self.object.pk})


class TaskNotificationListView(LoginRequiredMixin, ListView):
    model = TaskNotification
    template_name = 'pms/task_notifications.html'
    context_object_name = 'task_notifications'

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'manager':
            return TaskNotification.objects.all()
        elif user.user_type == 'team_member':
            return TaskNotification.objects.filter(task__assigned_to=user)
        else:
            return TaskNotification.objects.none()


# Client Project Approval View
class ProjectApprovalView(LoginRequiredMixin, ClientRequiredMixin, UpdateView):
    model = Project
    fields = ['status']
    template_name = 'pms/project_approval.html'
    success_url = reverse_lazy('project-list')

    def get_queryset(self):
        return Project.objects.filter(
            client=self.request.user, status='pending')

    def form_valid(self, form):
        response = super().form_valid(form)
        status = form.cleaned_data['status']
        messages.success(
            self.request,
            f'Project has been {status}.'
        )
        return response
    

class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'pms/payment_list.html'
    context_object_name = 'payments'

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'manager':
            return Payment.objects.all()
        elif user.user_type == 'client':
            return Payment.objects.filter(milestone__project__client=user)
        return Payment.objects.none()


class PaymentCreateView(LoginRequiredMixin, ClientRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'pms/payment_form.html'

    def get_milestone(self):
        print(self.kwargs['milestone_pk'])  # Debugging line
        return get_object_or_404(
            Milestone,
            pk=self.kwargs['milestone_pk'],
            project__client=self.request.user
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['milestone'] = self.get_milestone()
        print(kwargs)  # Debugging line
        return kwargs

    def form_valid(self, form):
        milestone = self.get_milestone()
        print(milestone.is_paid)  # Debugging line

        if milestone.is_paid:
            messages.error(self.request, 'This milestone has already been paid.')
            print("Redirecting because milestone is already paid")  # Debugging line
            return redirect('project-detail', pk=milestone.project.pk)
        
        else:
            milestone.is_paid = True
            milestone.save()
        
        print(milestone.is_paid)
        form.instance.milestone = milestone
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Payment proof uploaded successfully. Waiting for manager verification.'
        )
        return response
    
    def form_invalid(self, form):
        print("Form errors:", form.errors)  # Debugging line
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy(
            'project-detail',
            kwargs={'pk': self.object.milestone.project.pk}
        )


class PaymentVerificationView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = Payment
    fields = ['status', 'notes']
    template_name = 'pms/payment_verification.html'

    def form_valid(self, form):
        
        payment = form.instance
        print(payment.milestone.is_paid)
        if form.cleaned_data['status'] == 'verified':
            payment.verified_at = timezone.now()
            payment.verified_by = self.request.user
            payment.milestone.is_paid = True
            payment.milestone.save()
            messages.success(self.request, 'Payment verified successfully.')
        elif form.cleaned_data['status'] == 'rejected':
            messages.warning(self.request, 'Payment proof rejected.')
        
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'payments-list'
        )