from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, UserViewSet, GroupViewSet


router = DefaultRouter()

router.register("departments", DepartmentViewSet)
router.register("users", UserViewSet)
router.register("groups", GroupViewSet)


urlpatterns = [
    path("", include(router.urls)),
]