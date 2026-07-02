from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate

from .models import Employee
from .serializers import (
    EmployeeSerializer,
    EmployeeUpdateSerializer,
    RegisterSerializer,
)
from .permissions import IsHROrManager, IsOwnerOrHROrManager


# ─────────────────────────────────────────────
# 1. REGISTER  (POST /api/register/)
# ─────────────────────────────────────────────
class RegisterView(APIView):
    """
    Public endpoint — anyone can register.
    POST: Create a new user + employee profile.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            employee = serializer.save()
            return Response(
                {
                    "message": "Registration successful!",
                    "employee_id": employee.id,
                    "username": employee.user.username,
                    "role": employee.role,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
# 2. ALL EMPLOYEES LIST  (GET/POST /api/employees/)
#    → Only HR and Manager can access
# ─────────────────────────────────────────────
class EmployeeListView(APIView):
    """
    GET: List all employees.
    POST: List all employees by passing 'username' and 'password' in JSON body.
    """
    # AllowAny so we can check credentials manually in POST
    permission_classes = [AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            if request.user.employee.role not in ['hr', 'manager']:
                return Response({"error": "Only HR and Managers can view this."}, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            return Response({"error": "Invalid employee profile"}, status=status.HTTP_403_FORBIDDEN)

        employees = Employee.objects.select_related('user').all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"error": "Please provide 'username' and 'password' in the body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check credentials manually
        user = authenticate(username=username, password=password)
        if user is not None:
            try:
                role = user.employee.role
            except Exception:
                return Response({"error": "User does not have an employee profile."}, status=status.HTTP_403_FORBIDDEN)

            if role in ['hr', 'manager']:
                employees = Employee.objects.select_related('user').all()
                serializer = EmployeeSerializer(employees, many=True)
                return Response(serializer.data)
            else:
                return Response(
                    {"error": "Access denied. Only HR and Managers can view all employees."},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)


# ─────────────────────────────────────────────
# 3. SINGLE EMPLOYEE DETAIL  (GET/PUT /api/employees/<id>/)
#    → HR/Manager can access any employee
#    → Employee can access only their own profile
# ─────────────────────────────────────────────
class EmployeeDetailView(APIView):
    """
    GET:  View employee detail.
    PUT:  Update employee detail.

    Access rules:
      - HR / Manager  →  can view/update ANY employee.
      - Employee      →  can view/update ONLY their own profile.
      - Employee updates are limited to phone & address only.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrHROrManager]

    def get_object(self, pk):
        try:
            return Employee.objects.select_related('user').get(pk=pk)
        except Employee.DoesNotExist:
            return None

    def get(self, request, pk):
        employee = self.get_object(pk)
        if employee is None:
            return Response(
                {"error": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check object-level permission
        permission = IsOwnerOrHROrManager()
        if not permission.has_object_permission(request, self, employee):
            return Response(
                {"error": "You can only view your own profile."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)

    def put(self, request, pk):
        employee = self.get_object(pk)
        if employee is None:
            return Response(
                {"error": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check object-level permission
        permission = IsOwnerOrHROrManager()
        if not permission.has_object_permission(request, self, employee):
            return Response(
                {"error": "You can only update your own profile."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # HR/Manager → can update all fields
        # Employee   → can only update phone & address
        if request.user.employee.role in ['hr', 'manager']:
            serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        else:
            serializer = EmployeeUpdateSerializer(employee, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Profile updated successfully!",
                    "data": EmployeeSerializer(employee).data,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
# 4. MY PROFILE  (GET/PUT /api/profile/)
#    → Any logged-in employee can see their own profile
# ─────────────────────────────────────────────
class MyProfileView(APIView):
    """
    Shortcut for employees to access their own profile
    without needing to know their employee ID.

    GET:  View own profile.
    PUT:  Update own profile (phone & address only).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            employee = request.user.employee
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)

    def put(self, request):
        try:
            employee = request.user.employee
        except Employee.DoesNotExist:
            return Response(
                {"error": "Employee profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Employees can only update phone & address
        if request.user.employee.role in ['hr', 'manager']:
            serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        else:
            serializer = EmployeeUpdateSerializer(employee, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Profile updated successfully!",
                    "data": EmployeeSerializer(employee).data,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
