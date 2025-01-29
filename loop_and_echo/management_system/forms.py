from django import forms
from .models import Project, Milestone, Task, Payment

from user.models import CustomUser


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title', 'description', 'total_price', 'client')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        manager = kwargs.pop('manager', None)
        super().__init__(*args, **kwargs)
        if manager:
            self.fields['client'].queryset = CustomUser.objects.filter(user_type='client')


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ('title', 'description', 'deadline')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'assigned_to', 'deadline')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(user_type='team_member')


class TaskStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('status',)
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop('user_type', None)
        super().__init__(*args, **kwargs)

        if user_type == 'team_member':
            self.fields['status'].choices = [
                ('not_started', 'Not Started'),
                ('started', 'Started'),
                ('completed', 'Completed')
            ]
        elif user_type == 'manager':
            self.fields['status'].choices = [
                ('completed', 'Completed'),
                ('finalized', 'Finalized'),
                ('rejected', 'Rejected')
            ]


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('amount', 'payment_proof')
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_proof': forms.FileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, milestone=None, **kwargs):
        super().__init__(*args, **kwargs)
        if milestone:
            self.fields['amount'].initial = milestone.payable_amount
            self.fields['amount'].widget.attrs['readonly'] = False