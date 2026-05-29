from django.db.models import Q
from accounts.models import DataAccessRequest


class VisibilityMixin:

    def get_queryset(self):

        user = self.request.user
        queryset = super().get_queryset()

        # Always isolate organization
        queryset = queryset.filter(organization=user.organization)

        # Super admin
        if user.is_superuser:
            return queryset

        filters = Q()

        # Own data
        filters |= Q(owner=user) | Q(created_by=user)

        # Approved access
        approved_requests = DataAccessRequest.objects.filter(
            requester=user,
            status="approved"
        )

        # User access
        user_ids = approved_requests.values_list(
            "target_user_id",
            flat=True
        )

        filters |= Q(owner_id__in=user_ids)

        # Group access
        group_ids = approved_requests.values_list(
            "target_group_id",
            flat=True
        )

        filters |= Q(owner__groups__id__in=group_ids)

        # Department access
        department_ids = approved_requests.values_list(
            "target_department_id",
            flat=True
        )

        filters |= Q(owner__groups__department_id__in=department_ids)

        return queryset.filter(filters).distinct()