from rest_framework import serializers
from .models import Activity, ActivityType


class ActivityTypeSerializer(serializers.ModelSerializer):
    activity_count = serializers.SerializerMethodField()

    class Meta:
        model = ActivityType
        fields = ["id", "name", "description", "is_active", "activity_count", "created_at"]
        read_only_fields = ["created_at"]
    
    def get_activity_count(self, obj):
        return obj.activities.filter(is_deleted=False).count()


class ActivitySerializer(serializers.ModelSerializer):
    owner_email = serializers.CharField(source="owner.email", read_only=True)
    activity_type_name = serializers.CharField(source="activity_type.name", read_only=True, allow_null=True)
    lead_title = serializers.CharField(source="lead.title", read_only=True, allow_null=True)
    contact_name = serializers.SerializerMethodField()
    deal_name = serializers.CharField(source="deal.name", read_only=True, allow_null=True)
    
    class Meta:
        model = Activity
        fields = [
            "id", "title", "activity_type", "activity_type_name", "owner", "owner_email",
            "lead", "lead_title", "contact", "contact_name", "deal", "deal_name",
            "notes", "activity_date", "next_followup_date", "duration_minutes",
            "location", "meeting_link", "organization", "status",
            "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at", "organization"]
    
    def get_contact_name(self, obj):
        if obj.contact:
            return f"{obj.contact.first_name} {obj.contact.last_name}".strip()
        return None


class ActivityDetailSerializer(ActivitySerializer):
    owner_details = serializers.StringRelatedField(source="owner", read_only=True)
    
    class Meta(ActivitySerializer.Meta):
        fields = ActivitySerializer.Meta.fields + ["owner_details"]


class ActivityTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityType
        fields = ["id", "name", "description", "is_active"]