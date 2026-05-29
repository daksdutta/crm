from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Company
from .serializers import CompanySerializer, CompanyDetailSerializer
from .services import CompanyService
from core.mixins import VisibilityMixin


class CompanyViewSet(VisibilityMixin, viewsets.ModelViewSet):
    """
    Company CRUD operations
    """
    queryset = Company.objects.filter(is_deleted=False)
    serializer_class = CompanySerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["industry", "owner"]
    search_fields = ["name", "website", "industry"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CompanyDetailSerializer
        return CompanySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related("owner").prefetch_related("contacts", "deals")

    def perform_create(self, serializer):
        serializer.validated_data["organization"] = self.request.user.organization
        serializer.validated_data["owner"] = self.request.user
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        CompanyService.delete_company(instance)
    
    @action(detail=True, methods=["get"])
    def contacts(self, request, pk=None):
        """Get all contacts for a company"""
        company = self.get_object()
        from contacts.serializers import ContactSerializer
        contacts = company.contacts.filter(is_deleted=False)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def deals(self, request, pk=None):
        """Get all deals for a company"""
        company = self.get_object()
        from deals.serializers import DealListSerializer
        deals = company.deals.filter(is_deleted=False)
        serializer = DealListSerializer(deals, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def change_owner(self, request, pk=None):
        """Change company owner"""
        company = self.get_object()
        new_owner_id = request.data.get("owner_id")
        
        if not new_owner_id:
            return Response(
                {"detail": "owner_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from accounts.models import User
        try:
            new_owner = User.objects.get(id=new_owner_id, organization=company.organization, is_deleted=False)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid owner"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        company.owner = new_owner
        company.save()
        
        return Response(
            CompanyDetailSerializer(company).data,
            status=status.HTTP_200_OK
        )