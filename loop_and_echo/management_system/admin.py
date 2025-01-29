from django.contrib import admin
from .models import Project, Milestone, Task, TaskNotification, Payment, Document

admin.site.register(Project)
admin.site.register(Milestone)
admin.site.register(Task)
admin.site.register(TaskNotification)
admin.site.register(Payment)
admin.site.register(Document)
