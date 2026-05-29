from rest_framework.routers import DefaultRouter
from .views import PipelineViewSet, PipelineStageViewSet, DealViewSet

router = DefaultRouter()
router.register(r"pipelines", PipelineViewSet, basename="pipeline")
router.register(r"stages", PipelineStageViewSet, basename="pipelinestage")
router.register(r"deals", DealViewSet, basename="deal")

urlpatterns = router.urls