from rest_framework import permissions
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from BankingBackend.constant import BANK_MANAGER, EMPLOYEE, CUSTOMER

class IsEmployee(permissions.BasePermission):
    """"""
    def has_permission(self, request, view):
        """
        Should simply return, or raise a 403 response.
        """
        if request.user.user_type not in [EMPLOYEE, BANK_MANAGER]:
            raise PermissionDenied
        return True


class IsCustomer(permissions.BasePermission):
    """"""
    def has_permission(self, request, view):
        """
        Should simply return, or raise a 403 response.
        """
        if request.user.user_type != CUSTOMER:
            raise PermissionDenied
        return True


class IsBankManager(permissions.BasePermission):
    """"""
    def has_permission(self, request, view):
        """
        Should simply return, or raise a 403 response.
        """
        if request.user.user_type != BANK_MANAGER:
            raise PermissionDenied
        return True
