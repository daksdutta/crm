from rest_framework import serializers
from .models import Lead


class LeadSerializer(serializers.ModelSerializer):
    contact_name = serializers.CharField(source="contact.get_full_name", read_only=True)
    owner_email = serializers.CharField(source="owner.email", read_only=True)
    
    class Meta:
        model = Lead
        fields = [
            "id", "title", "contact", "contact_name", "owner", "owner_email",
            "status", "source", "notes", "organization", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at", "organization"]


class LeadDetailSerializer(LeadSerializer):
    activities = serializers.SerializerMethodField()
    
    class Meta(LeadSerializer.Meta):
        fields = LeadSerializer.Meta.fields + ["activities"]
    
    def get_activities(self, obj):
        from activities.serializers import ActivitySerializer
        activities = obj.activities.filter(is_deleted=False).order_by("-activity_date")[:5]
        return ActivitySerializer(activities, many=True).data


class LeadStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=["new", "contacted", "qualified", "lost", "converted"]
    )