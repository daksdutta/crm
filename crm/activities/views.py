from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone

from .models import Activity, ActivityType
from .serializers import (
    ActivitySerializer,
    ActivityTypeSerializer,
    ActivityDetailSerializer,
    ActivityTypeListSerializer
)
from .services import ActivityService, ActivityTypeService
from core.mixins import VisibilityMixin


class ActivityTypeViewSet(viewsets.ModelViewSet):
    """
    Activity Type management
    """
    queryset = ActivityType.objects.filter(is_deleted=False)
    serializer_class = ActivityTypeSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return ActivityTypeListSerializer
        return ActivityTypeSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class ActivityViewSet(VisibilityMixin, viewsets.ModelViewSet):
    """
    Activity CRUD operations and tracking
    """
    queryset = Activity.objects.filter(is_deleted=False)
    serializer_class = ActivitySerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["activity_type", "lead", "contact", "deal", "owner", "status"]
    search_fields = ["title", "notes", "contact__first_name", "contact__last_name"]
    ordering_fields = ["created_at", "activity_date", "next_followup_date"]
    ordering = ["-activity_date"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ActivityDetailSerializer
        return ActivitySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            "activity_type", "owner", "lead", "contact", "deal"
        ).prefetch_related()

    def perform_create(self, serializer):
        serializer.validated_data["organization"] = self.request.user.organization
        serializer.validated_data["owner"] = self.request.user
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        ActivityService.delete_activity(instance)
    
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark activity as completed"""
        activity = self.get_object()
        ActivityService.complete_activity(activity)
        return Response(
            ActivityDetailSerializer(activity).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel activity"""
        activity = self.get_object()
        ActivityService.cancel_activity(activity)
        return Response(
            ActivityDetailSerializer(activity).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """Get upcoming activities for user"""
        now = timezone.now()
        activities = self.get_queryset().filter(
            owner=request.user,
            activity_date__gte=now,
            status__in=["scheduled", "in_progress"]
        ).order_by("activity_date")[:10]
        
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def followup_due(self, request):
        """Get activities with follow-up due"""
        now = timezone.now()
        activities = self.get_queryset().filter(
            next_followup_date__lte=now,
            status__in=["completed", "no_show"]
        ).order_by("next_followup_date")
        
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"])
    def by_status(self, request):
        """Get activities grouped by status"""
        queryset = self.filter_queryset(self.get_queryset())
        
        statuses = [s[0] for s in Activity.ACTIVITY_STATUS_CHOICES]
        data = {}
        
        for status_val in statuses:
            activities = queryset.filter(status=status_val)
            data[status_val] = {
                "count": activities.count(),
                "activities": ActivitySerializer(activities, many=True).data
            }
        
        return Response(data)
    
    @action(detail=False, methods=["get"])
    def by_type(self, request):
        """Get activities grouped by type"""
        queryset = self.filter_queryset(self.get_queryset())
        
        data = {}
        for activity_type in ActivityType.objects.filter(is_deleted=False, is_active=True):
            activities = queryset.filter(activity_type=activity_type)
            data[activity_type.name] = {
                "count": activities.count(),
                "activities": ActivitySerializer(activities, many=True).data
            }
        
        return Response(data)
    
    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get activity analytics"""
        queryset = self.filter_queryset(self.get_queryset())
        
        today = timezone.now().date()
        total_activities = queryset.count()
        today_activities = queryset.filter(activity_date__date=today).count()
        completed = queryset.filter(status="completed").count()
        scheduled = queryset.filter(status="scheduled").count()
        cancelled = queryset.filter(status="cancelled").count()
        
        analytics = {
            "total_activities": total_activities,
            "today_activities": today_activities,
            "by_status": {
                "scheduled": scheduled,
                "in_progress": queryset.filter(status="in_progress").count(),
                "completed": completed,
                "cancelled": cancelled,
                "no_show": queryset.filter(status="no_show").count(),
            },
            "by_type": {},
            "by_owner": [],
            "completion_rate": (completed / total_activities * 100) if total_activities > 0 else 0
        }
        
        # By type
        for activity_type in ActivityType.objects.filter(is_deleted=False, is_active=True):
            count = queryset.filter(activity_type=activity_type).count()
            if count > 0:
                analytics["by_type"][activity_type.name] = count
        
        # By owner
        for owner_data in queryset.values("owner__email").annotate(count=Count("id")):
            if owner_data["owner__email"]:
                analytics["by_owner"].append({
                    "owner": owner_data["owner__email"],
                    "count": owner_data["count"]
                })
        
        return Response(analytics)