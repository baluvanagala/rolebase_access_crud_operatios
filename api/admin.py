from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'phone', 'date_of_joining', 'salary']
    list_filter = ['role', 'department']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
