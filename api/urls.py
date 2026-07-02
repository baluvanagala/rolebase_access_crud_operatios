from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('register/', views.RegisterView.as_view(), name='register'),

    # HR / Manager → list all employees
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),

    # HR / Manager → any employee | Employee → own profile only
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),

    # Any logged-in user → their own profile
    path('profile/', views.MyProfileView.as_view(), name='my-profile'),
]
