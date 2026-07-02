from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Employee


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the Django User model (nested inside Employee)."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username']


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Full employee serializer.
    - Shows nested user info (username, email, name).
    - Used by HR/Manager to view all employees.
    - Used by Employee to view their own profile.
    """

    user = UserSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'role', 'role_display',
            'department', 'phone', 'address',
            'date_of_joining', 'salary',
        ]
        read_only_fields = ['id', 'role']  # Only admin can change role


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for employees to update their own profile.
    They can only edit: phone, address (NOT role, salary, department).
    """

    class Meta:
        model = Employee
        fields = ['phone', 'address']


class RegisterSerializer(serializers.Serializer):
    """Serializer for registering a new user + employee profile."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=30, required=False, default='')
    last_name = serializers.CharField(max_length=30, required=False, default='')
    role = serializers.ChoiceField(choices=Employee.ROLE_CHOICES, default='employee')
    department = serializers.CharField(max_length=100, required=False, default='')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        employee = Employee.objects.create(
            user=user,
            role=validated_data.get('role', 'employee'),
            department=validated_data.get('department', ''),
        )
        return employee
