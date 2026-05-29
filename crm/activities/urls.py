from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivityViewSet, ActivityTypeViewSet

router = DefaultRouter()

router.register("activity-types", ActivityTypeViewSet, basename="activity-type")
router.register("", ActivityViewSet, basename="activity")

urlpatterns = [
    path("", include(router.urls)),
]
