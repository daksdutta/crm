from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Contact
from .serializers import ContactSerializer, ContactDetailSerializer
from .services import ContactService
from core.mixins import VisibilityMixin


class ContactViewSet(VisibilityMixin, viewsets.ModelViewSet):
    """
    Contact CRUD operations
    """
    queryset = Contact.objects.filter(is_deleted=False)
    serializer_class = ContactSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["company", "owner"]
    search_fields = ["first_name", "last_name", "email", "phone", "company__name"]
    ordering_fields = ["created_at", "first_name", "last_name"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ContactDetailSerializer
        return ContactSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related("company", "owner").prefetch_related("leads", "activities")

    def perform_create(self, serializer):
        serializer.validated_data["organization"] = self.request.user.organization
        serializer.validated_data["owner"] = self.request.user
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        ContactService.delete_contact(instance)
    
    @action(detail=True, methods=["get"])
    def leads(self, request, pk=None):
        """Get all leads for a contact"""
        contact = self.get_object()
        from leads.serializers import LeadSerializer
        leads = contact.leads.filter(is_deleted=False)
        serializer = LeadSerializer(leads, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def activities(self, request, pk=None):
        """Get all activities for a contact"""
        contact = self.get_object()
        from activities.serializers import ActivitySerializer
        activities = contact.activities.filter(is_deleted=False).order_by("-activity_date")
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def deals(self, request, pk=None):
        """Get all deals for a contact"""
        contact = self.get_object()
        from deals.serializers import DealListSerializer
        deals = contact.deals.filter(is_deleted=False)
        serializer = DealListSerializer(deals, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def change_owner(self, request, pk=None):
        """Change contact owner"""
        contact = self.get_object()
        new_owner_id = request.data.get("owner_id")
        
        if not new_owner_id:
            return Response(
                {"detail": "owner_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from accounts.models import User
        try:
            new_owner = User.objects.get(id=new_owner_id, organization=contact.organization, is_deleted=False)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid owner"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        contact.owner = new_owner
        contact.save()
        
        return Response(
            ContactDetailSerializer(contact).data,
            status=status.HTTP_200_OK
        )