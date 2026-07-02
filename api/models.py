from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):
    """
    Employee model linked to Django's built-in User.
    Each employee has a role: employee, hr, or manager.
    """

    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('hr', 'HR'),
        ('manager', 'Manager'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    class Meta:
        ordering = ['user__username']
