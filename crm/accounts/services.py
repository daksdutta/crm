from django.core.exceptions import PermissionDenied
from django.db import transaction

from accounts.repositories import (
    UserRepository,
    DepartmentRepository,
    AccessRequestRepository,
)


class UserService:

    def __init__(self):
        self.repo = UserRepository()

    def create_user(self, data):

        password = data.pop("password")
        user = self.repo.create(**data)
        user.set_password(password)
        self.repo.save(user)

        return user

    def update_user(self, user, data):

        for field, value in data.items():
            setattr(user, field, value)

        self.repo.save(user)
        return user

    def delete_user(self, user):

        user.is_deleted = True
        self.repo.save(user)
        return user


class DepartmentService:

    def __init__(self):
        self.repo = DepartmentRepository()

    def create_department(self, data):
        return self.repo.create(**data)

    def update_department(self, department, data):

        for field, value in data.items():
            setattr(department, field, value)

        self.repo.save(department)

        return department

    def delete_department(self, department):

        department.is_deleted = True
        self.repo.save(department)

        return department


class AccessRequestService:

    def __init__(self):
        self.repo = AccessRequestRepository()

    def create_request(self, data):
        return self.repo.create(**data)

    @transaction.atomic
    def approve_request(self, request_obj, approver):

        # permission check
        if not approver.has_perm("accounts.approve_access_request"):
            raise PermissionDenied("You cannot approve access requests")

        # prevent approving own request
        if request_obj.requester == approver:
            raise PermissionDenied("You cannot approve your own request")

        request_obj.status = "approved"
        request_obj.approved_by = approver

        self.repo.save(request_obj)

        return request_obj

    def reject_request(self, request_obj, approver):

        if not approver.has_perm("accounts.approve_access_request"):
            raise PermissionDenied("You cannot reject access requests")

        request_obj.status = "rejected"
        request_obj.approved_by = approver

        self.repo.save(request_obj)

        return request_obj