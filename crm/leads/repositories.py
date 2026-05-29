from .models import Lead
from accounts.models import User


class LeadRepository:

    @staticmethod
    def get_by_id(lead_id):
        return Lead.objects.filter(id=lead_id, is_deleted=False).first()

    @staticmethod
    def get_by_org(organization):
        return Lead.objects.filter(organization=organization, is_deleted=False)

    @staticmethod
    def get_by_status(status):
        return Lead.objects.filter(status=status, is_deleted=False)

    @staticmethod
    def list():
        return Lead.objects.filter(is_deleted=False)

    @staticmethod
    def create(**data):
        return Lead.objects.create(**data)

    @staticmethod
    def save(lead):
        lead.save()
        return lead

    @staticmethod
    def delete(lead):
        lead.is_deleted = True
        return LeadRepository.save(lead)

    @staticmethod
    def get_user_by_id(user_id):
        return User.objects.filter(id=user_id, is_deleted=False).first()