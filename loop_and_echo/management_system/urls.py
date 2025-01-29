from django.urls import path
from . import views

urlpatterns = [

    path('', views.ProjectListView.as_view(), name='project-list'),
    path('project/new/', views.ProjectCreateView.as_view(), name='project-create'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('project/<int:pk>/update/', views.ProjectUpdateView.as_view(), name='project-update'),
    path('project/<int:pk>/approve/', views.ProjectApprovalView.as_view(), name='project-approve'),
    
    path('project/<int:project_pk>/milestone/new/', 
         views.MilestoneCreateView.as_view(), name='milestone-create'),
    path('milestone/<int:pk>/update/', 
         views.MilestoneUpdateView.as_view(), name='milestone-update'),
    path('milestone/<int:pk>/',
         views.MilestoneDetailView.as_view(), name='milestone-detail'),
    path('milestone/<int:milestone_pk>/task/new/',
         views.TaskCreateView.as_view(), name='task-create'),
    path('milestone/<int:pk>/delete/',
         views.MilestoneDeleteView.as_view(), name='milestone-delete'),
    path('task/<int:pk>/update/',
         views.TaskUpdateView.as_view(), name='task-update'),
    path('tasks/',
         views.TaskListView.as_view(), name='task-list'),
    path('task/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task-delete'),
    path('task/notifications/', views.TaskNotificationListView.as_view(), name='task-notificaiton-list'),
    path('milestone/<int:milestone_pk>/payment/create/',
         views.PaymentCreateView.as_view(), name='payment-create'),
    path('payment/<int:pk>/verify/',
         views.PaymentVerificationView.as_view(), name='payment-verify'),
    path('payments/', views.PaymentListView.as_view(), name='payments-list'),

]