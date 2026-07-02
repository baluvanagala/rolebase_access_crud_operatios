from rest_framework.permissions import BasePermission


class IsHROrManager(BasePermission):
    """
    Allow access only to users with role 'hr' or 'manager'.
    These users can view/edit ALL employee records.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'employee') and request.user.employee.role in ['hr', 'manager']


class IsOwnerOrHROrManager(BasePermission):
    """
    - HR / Manager  →  can access ANY employee record.
    - Employee      →  can access ONLY their own record.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return hasattr(request.user, 'employee')

    def has_object_permission(self, request, view, obj):
        # HR and Manager can access any employee
        if request.user.employee.role in ['hr', 'manager']:
            return True
        # Employee can only access their own profile
        return obj.user == request.user
