from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import Permission


class GlobalPermission(models.Model):

    class Meta:
        permissions = [
            ("view_department_data", "Can view department data"),
            ("approve_access_request", "Can approve access requests"),
        ]


# NEW: tenant model
class Organization(BaseModel):

    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class Department(BaseModel):

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,related_name="departments",db_index=True)     # Department belongs to organization

    def __str__(self):
        return self.name


class User(AbstractUser, BaseModel):

    username = None
    email = models.EmailField(unique=True)
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,related_name="users",db_index=True)
    department = models.ForeignKey(Department,on_delete=models.SET_NULL,null=True,blank=True)
    phone = models.CharField(max_length=20, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email

class Group(BaseModel):

    name = models.CharField(max_length=255)

    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,related_name="groups",db_index=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,related_name="groups",db_index=True)
    users = models.ManyToManyField(User,related_name="crm_groups",blank=True)
    permissions = models.ManyToManyField(Permission,blank=True,related_name="custom_groups")

    class Meta:
        unique_together = ("department", "name")

    def __str__(self):
        return f"{self.department.name} - {self.name}"


class DataAccessRequest(BaseModel):

    ACCESS_TYPE = [
        ("user", "User"),
        ("group", "Group"),
        ("department", "Department"),
    ]

    requester = models.ForeignKey( User,on_delete=models.CASCADE,related_name="access_requests")
    access_type = models.CharField(max_length=20,choices=ACCESS_TYPE)
    target_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name="requested_user_access")
    target_department = models.ForeignKey(Department,on_delete=models.CASCADE)
    target_group = models.ForeignKey("Group",on_delete=models.CASCADE,null=True,blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected")
        ],
        default="pending"
    )

    approved_by = models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL,related_name="approved_requests")

    class Meta:

        constraints = [

            # Only one target allowed
            models.CheckConstraint(
                condition=(
                    (
                        models.Q(target_user__isnull=False) &
                        models.Q(target_group__isnull=True) &
                        models.Q(target_department__isnull=True)
                    ) |
                    (
                        models.Q(target_user__isnull=True) &
                        models.Q(target_group__isnull=False) &
                        models.Q(target_department__isnull=True)
                    ) |
                    (
                        models.Q(target_user__isnull=True) &
                        models.Q(target_group__isnull=True) &
                        models.Q(target_department__isnull=False)
                    )
                ),
                name="only_one_access_target"
            ),

            # prevent duplicate user access requests
            models.UniqueConstraint(
                fields=["requester", "target_user"],
                name="unique_user_access_request"
            ),

            # prevent duplicate group requests
            models.UniqueConstraint(
                fields=["requester", "target_group"],
                name="unique_group_access_request"
            ),

            # prevent duplicate department requests
            models.UniqueConstraint(
                fields=["requester", "target_department"],
                name="unique_department_access_request"
            ),
        ]
        
    def __str__(self):
        return f"{self.requester} → {self.target_department}"