from .models import User, Department, DataAccessRequest


class UserRepository:

    def get_by_id(self, user_id):
        return User.objects.filter(id=user_id, is_deleted=False).first()

    def get_by_email(self, email):
        return User.objects.filter(email=email, is_deleted=False).first()

    def list(self):
        return User.objects.filter(is_deleted=False)

    def create(self, **data):
        return User.objects.create(**data)

    def save(self, user):
        user.save()
        return user


class DepartmentRepository:

    def get_by_id(self, department_id):
        return Department.objects.filter(id=department_id, is_deleted=False).first()

    def list(self):
        return Department.objects.filter(is_deleted=False)

    def create(self, **data):
        return Department.objects.create(**data)

    def save(self, department):
        department.save()
        return department


class AccessRequestRepository:

    def create(self, **data):
        return DataAccessRequest.objects.create(**data)

    def get_by_id(self, request_id):
        return DataAccessRequest.objects.filter(id=request_id).first()

    def get_pending(self):
        return DataAccessRequest.objects.filter(status="pending")

    def save(self, request_obj):
        request_obj.save()
        return request_obj