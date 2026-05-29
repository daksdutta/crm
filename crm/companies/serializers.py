from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    owner_email = serializers.CharField(source="owner.email", read_only=True)
    contact_count = serializers.SerializerMethodField()
    deal_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            "id", "name", "industry", "website", "owner", "owner_email",
            "organization", "contact_count", "deal_count", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at", "organization"]
    
    def get_contact_count(self, obj):
        return obj.contacts.filter(is_deleted=False).count()
    
    def get_deal_count(self, obj):
        return obj.deals.filter(is_deleted=False).count()


class CompanyDetailSerializer(CompanySerializer):
    contacts = serializers.SerializerMethodField()
    deals_summary = serializers.SerializerMethodField()
    
    class Meta(CompanySerializer.Meta):
        fields = CompanySerializer.Meta.fields + ["contacts", "deals_summary"]
    
    def get_contacts(self, obj):
        from contacts.serializers import ContactSerializer
        contacts = obj.contacts.filter(is_deleted=False)
        return ContactSerializer(contacts, many=True).data
    
    def get_deals_summary(self, obj):
        deals = obj.deals.filter(is_deleted=False)
        return {
            "total": deals.count(),
            "value": float(deals.aggregate(total=serializers.Sum("amount"))["total"] or 0)
        }