from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.db.models import Q, Sum, Count, Avg
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import VisibilityMixin
from .models import Pipeline, PipelineStage, Deal
from .serializers import (
    PipelineSerializer,
    PipelineStageSerializer,
    DealSerializer,
    DealListSerializer,
    DealDetailSerializer
)
from .services import (
    PipelineService,
    PipelineStageService,
    DealService
)
from .repositories import (
    PipelineRepository,
    PipelineStageRepository,
    DealRepository
)


class PipelineViewSet(viewsets.ModelViewSet):
    """
    Pipeline CRUD operations
    """
    serializer_class = PipelineSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
    
    def get_queryset(self):
        return Pipeline.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False
        ).order_by("-created_at")
    
    def perform_create(self, serializer):
        serializer.validated_data["created_by"] = self.request.user
        serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        pipeline = self.get_object()
        try:
            PipelineService.delete(pipeline)
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=["get"])
    def analytics(self, request, pk=None):
        """Get pipeline analytics"""
        pipeline = self.get_object()
        stages = pipeline.stages.filter(is_deleted=False)
        
        analytics = {
            "total_deals": Deal.objects.filter(pipeline_stage__pipeline=pipeline, is_deleted=False).count(),
            "total_value": Deal.objects.filter(
                pipeline_stage__pipeline=pipeline,
                is_deleted=False
            ).aggregate(total=Sum("amount"))["total"] or 0,
            "stages": []
        }
        
        for stage in stages:
            stage_deals = Deal.objects.filter(pipeline_stage=stage, is_deleted=False)
            analytics["stages"].append({
                "name": stage.name,
                "deal_count": stage_deals.count(),
                "total_value": stage_deals.aggregate(total=Sum("amount"))["total"] or 0,
                "avg_value": stage_deals.aggregate(avg=Avg("amount"))["avg"] or 0
            })
        
        return Response(analytics)


class PipelineStageViewSet(viewsets.ModelViewSet):
    """
    Pipeline Stage management
    """
    serializer_class = PipelineStageSerializer
    
    def get_queryset(self):
        return PipelineStage.objects.filter(
            pipeline__organization=self.request.user.organization,
            is_deleted=False
        ).order_by("order")
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=False, methods=["post"])
    def reorder(self, request):
        """Reorder stages within a pipeline"""
        pipeline_id = request.data.get("pipeline_id")
        stage_orders = request.data.get("stages", [])
        
        if not pipeline_id or not stage_orders:
            return Response(
                {"detail": "pipeline_id and stages are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pipeline = PipelineRepository.get_by_id(pipeline_id)
        except:
            return Response(
                {"detail": "Pipeline not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            stages = PipelineStageService.reorder(pipeline, stage_orders)
            return Response(
                PipelineStageSerializer(stages, many=True).data,
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class DealViewSet(VisibilityMixin, viewsets.ModelViewSet):
    """
    Deal CRUD operations with filtering, analytics, and kanban view
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["pipeline_stage", "owner", "status", "company"]
    search_fields = ["name", "company__name", "contact__first_name", "contact__last_name"]
    ordering_fields = ["created_at", "expected_close_date", "amount"]
    ordering = ["-created_at"]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return Deal.objects.filter(
            organization=self.request.user.organization,
            is_deleted=False
        ).select_related(
            "owner", "created_by", "pipeline_stage", "company", "contact"
        )
    
    def get_serializer_class(self):
        if self.action == "list":
            return DealListSerializer
        elif self.action == "retrieve":
            return DealDetailSerializer
        return DealSerializer
    
    def perform_create(self, serializer):
        serializer.validated_data["created_by"] = self.request.user
        if "owner" not in serializer.validated_data:
            serializer.validated_data["owner"] = self.request.user
        serializer.save()
    
    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
    
    @action(detail=True, methods=["post"])
    def move_stage(self, request, pk=None):
        """Move deal to a different stage"""
        try:
            deal = self.get_object()
            new_stage_id = request.data.get("stage_id")
            
            if not new_stage_id:
                return Response(
                    {"detail": "stage_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                new_stage = PipelineStageRepository.get_by_id(new_stage_id)
            except:
                return Response(
                    {"detail": "Invalid stage"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            deal.pipeline_stage = new_stage
            deal.save()
            
            return Response(
                DealDetailSerializer(deal).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=["post"])
    def change_owner(self, request, pk=None):
        """Change deal owner"""
        try:
            deal = self.get_object()
            new_owner_id = request.data.get("owner_id")
            
            if not new_owner_id:
                return Response(
                    {"detail": "owner_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            from accounts.models import User
            try:
                new_owner = User.objects.get(id=new_owner_id, organization=deal.organization, is_deleted=False)
            except User.DoesNotExist:
                return Response(
                    {"detail": "Invalid owner"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            deal.owner = new_owner
            deal.save()
            
            return Response(
                DealDetailSerializer(deal).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=["get"])
    def kanban(self, request):
        """Get deals grouped by stage (Kanban view)"""
        pipeline_id = request.query_params.get("pipeline_id")
        
        if not pipeline_id:
            return Response(
                {"detail": "pipeline_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pipeline = Pipeline.objects.get(id=pipeline_id, organization=request.user.organization)
        except Pipeline.DoesNotExist:
            return Response(
                {"detail": "Pipeline not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        stages = pipeline.stages.filter(is_deleted=False).order_by("order")
        data = {
            "pipeline": PipelineSerializer(pipeline).data,
            "stages": []
        }
        
        for stage in stages:
            deals = Deal.objects.filter(
                pipeline_stage=stage,
                organization=request.user.organization,
                is_deleted=False
            )
            data["stages"].append({
                "stage": PipelineStageSerializer(stage).data,
                "deals": DealListSerializer(deals, many=True).data,
                "total_value": deals.aggregate(total=Sum("amount"))["total"] or 0
            })
        
        return Response(data)
    
    @action(detail=False, methods=["get"])
    def analytics(self, request):
        """Get deal analytics"""
        queryset = self.get_queryset()
        
        total_deals = queryset.count()
        total_value = queryset.aggregate(total=Sum("amount"))["total"] or 0
        open_deals = queryset.filter(status="OPEN").count()
        won_deals = queryset.filter(status="WON").count()
        lost_deals = queryset.filter(status="LOST").count()
        
        analytics = {
            "total_deals": total_deals,
            "total_value": float(total_value),
            "open_deals": open_deals,
            "won_deals": won_deals,
            "lost_deals": lost_deals,
            "avg_deal_value": float(queryset.aggregate(avg=Avg("amount"))["avg"] or 0),
            "by_owner": [],
            "by_status": {
                "OPEN": open_deals,
                "WON": won_deals,
                "LOST": lost_deals
            }
        }
        
        # By owner
        for owner_data in queryset.values("owner__email").annotate(
            count=Count("id"),
            total=Sum("amount"),
            avg=Avg("amount")
        ):
            analytics["by_owner"].append({
                "owner": owner_data["owner__email"],
                "deal_count": owner_data["count"],
                "total_value": float(owner_data["total"] or 0),
                "avg_value": float(owner_data["avg"] or 0)
            })
        
        return Response(analytics)
    
    @action(detail=False, methods=["post"])
    def bulk_update(self, request):
        """Bulk update deals"""
        deal_ids = request.data.get("deal_ids", [])
        new_stage_id = request.data.get("stage_id")
        new_owner_id = request.data.get("owner_id")
        
        if not deal_ids:
            return Response(
                {"detail": "deal_ids are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not new_stage_id and not new_owner_id:
            return Response(
                {"detail": "Either stage_id or owner_id must be provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deals = Deal.objects.filter(
            id__in=deal_ids,
            organization=request.user.organization,
            is_deleted=False
        )
        
        if new_stage_id:
            try:
                new_stage = PipelineStage.objects.get(id=new_stage_id)
                deals.update(pipeline_stage=new_stage)
            except PipelineStage.DoesNotExist:
                return Response(
                    {"detail": "Invalid stage"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        if new_owner_id:
            from accounts.models import User
            try:
                new_owner = User.objects.get(id=new_owner_id, organization=request.user.organization)
                deals.update(owner=new_owner)
            except User.DoesNotExist:
                return Response(
                    {"detail": "Invalid owner"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        updated_deals = Deal.objects.filter(id__in=deal_ids)
        return Response(
            DealListSerializer(updated_deals, many=True).data,
            status=status.HTTP_200_OK
        )