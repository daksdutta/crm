from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import Group

from .models import User, Department, DataAccessRequest
from .serializers import (
    UserSerializer,
    DepartmentSerializer,
    AccessRequestSerializer,
    GroupSerializer,
)

from .services import (
    UserService,
    DepartmentService,
    AccessRequestService,
)


class GroupViewSet(viewsets.ModelViewSet):

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class DepartmentViewSet(viewsets.ModelViewSet):

    queryset = Department.objects.filter(is_deleted=False)
    serializer_class = DepartmentSerializer

    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    service = DepartmentService()

    def perform_destroy(self, instance):
        self.service.delete_department(instance)


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["department", "groups"]
    search_fields = ["email", "phone"]
    ordering_fields = ["created_at"]

    service = UserService()

    def perform_create(self, serializer):
        self.service.create_user(serializer.validated_data)

    def perform_update(self, serializer):
        user = self.get_object()
        self.service.update_user(user, serializer.validated_data)

    def perform_destroy(self, instance):
        self.service.delete_user(instance)


class AccessRequestViewSet(viewsets.ModelViewSet):

    queryset = DataAccessRequest.objects.all()
    serializer_class = AccessRequestSerializer

    service = AccessRequestService()

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)

    @action(detail=True, methods=["patch"])
    def approve(self, request, pk=None):

        request_obj = self.get_object()

        self.service.approve_request(request_obj,approver=request.user)

        return Response(
            {"message": "Access request approved"},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"])
    def reject(self, request, pk=None):

        request_obj = self.get_object()

        self.service.reject_request(request_obj)

        return Response(
            {"message": "Access request rejected"},
            status=status.HTTP_200_OK,
        )