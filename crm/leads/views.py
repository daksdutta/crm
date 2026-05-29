from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db.models import Count

from .models import Lead
from .serializers import LeadSerializer, LeadDetailSerializer, LeadStatusUpdateSerializer
from .services import LeadService
from core.mixins import VisibilityMixin


class LeadViewSet(VisibilityMixin, viewsets.ModelViewSet):
    """
    Lead CRUD operations and lifecycle management
    """
    queryset = Lead.objects.filter(is_deleted=False)
    serializer_class = LeadSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["status", "owner", "source", "contact__company"]
    search_fields = ["title", "contact__first_name", "contact__last_name", "contact__email"]
    ordering_fields = ["created_at", "title", "status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LeadDetailSerializer
        return LeadSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related("contact", "owner").prefetch_related("activities")

    def perform_create(self, serializer):
        serializer.validated_data["organization"] = self.request.user.organization
        serializer.validated_data["owner"] = self.request.user
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        LeadService.delete_lead(instance)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        """Assign lead to a user"""
        lead = self.get_object()
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"detail": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            LeadService.assign_lead(lead, user_id)
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            LeadDetailSerializer(lead).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        """Change lead status"""
        lead = self.get_object()
        serializer = LeadStatusUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            LeadService.change_status(lead, serializer.validated_data["status"])
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            LeadDetailSerializer(lead).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def convert(self, request, pk=None):
        """Convert lead to deal"""
        lead = self.get_object()

        try:
            LeadService.convert_lead(lead)
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Lead converted successfully",
                "lead": LeadDetailSerializer(lead).data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=["get"])
    def by_status(self, request):
        """Get leads grouped by status"""
        queryset = self.filter_queryset(self.get_queryset())
        statuses = Lead.LEAD_STATUS
        
        data = {}
        for status_val, status_label in statuses:
            leads = queryset.filter(status=status_val)
            data[status_val] = {
                "label": status_label,
                "count": leads.count(),
                "leads": LeadSerializer(leads, many=True).data
            }
        
        return Response(data)
    
    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get lead analytics"""
        queryset = self.filter_queryset(self.get_queryset())
        
        total_leads = queryset.count()
        new_leads = queryset.filter(status="new").count()
        contacted = queryset.filter(status="contacted").count()
        qualified = queryset.filter(status="qualified").count()
        converted = queryset.filter(status="converted").count()
        lost = queryset.filter(status="lost").count()
        
        analytics = {
            "total_leads": total_leads,
            "by_status": {
                "new": new_leads,
                "contacted": contacted,
                "qualified": qualified,
                "converted": converted,
                "lost": lost
            },
            "conversion_rate": (converted / total_leads * 100) if total_leads > 0 else 0,
            "by_source": {},
            "by_owner": []
        }
        
        # By source
        for source_data in queryset.values("source").annotate(count=Count("id")):
            if source_data["source"]:
                analytics["by_source"][source_data["source"]] = source_data["count"]
        
        # By owner
        for owner_data in queryset.values("owner__email").annotate(count=Count("id")):
            if owner_data["owner__email"]:
                analytics["by_owner"].append({
                    "owner": owner_data["owner__email"],
                    "count": owner_data["count"]
                })
        
        return Response(analytics)