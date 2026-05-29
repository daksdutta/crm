from rest_framework import serializers
from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    owner_email = serializers.CharField(source="owner.email", read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Contact
        fields = [
            "id", "first_name", "last_name", "full_name", "email", "phone",
            "company", "company_name", "owner", "owner_email",
            "organization", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at", "organization"]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class ContactDetailSerializer(ContactSerializer):
    leads = serializers.SerializerMethodField()
    activities = serializers.SerializerMethodField()
    deals = serializers.SerializerMethodField()
    
    class Meta(ContactSerializer.Meta):
        fields = ContactSerializer.Meta.fields + ["leads", "activities", "deals"]
    
    def get_leads(self, obj):
        from leads.serializers import LeadSerializer
        leads = obj.leads.filter(is_deleted=False)
        return LeadSerializer(leads, many=True).data
    
    def get_activities(self, obj):
        from activities.serializers import ActivitySerializer
        activities = obj.activities.filter(is_deleted=False).order_by("-activity_date")[:10]
        return ActivitySerializer(activities, many=True).data
    
    def get_deals(self, obj):
        from deals.serializers import DealListSerializer
        deals = obj.deals.filter(is_deleted=False)
        return DealListSerializer(deals, many=True).data