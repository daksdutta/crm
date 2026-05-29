from .repositories import LeadRepository
from django.db import transaction
from django.core.exceptions import ValidationError


class LeadService:

    @staticmethod
    @transaction.atomic
    def create_lead(data, user):
        data["owner"] = user
        data["organization"] = user.organization
        return LeadRepository.create(**data)

    @staticmethod
    @transaction.atomic
    def update_lead(lead, data):
        for field, value in data.items():
            if field not in ["id", "organization", "created_at", "updated_at", "is_deleted"]:
                setattr(lead, field, value)
        return LeadRepository.save(lead)

    @staticmethod
    def delete_lead(lead):
        return LeadRepository.delete(lead)

    @staticmethod
    @transaction.atomic
    def assign_lead(lead, user_id):
        user = LeadRepository.get_user_by_id(user_id)
        if not user:
            raise ValidationError("User not found")
        lead.owner = user
        return LeadRepository.save(lead)

    @staticmethod
    @transaction.atomic
    def change_status(lead, new_status):
        if new_status not in ["new", "contacted", "qualified", "lost", "converted"]:
            raise ValidationError("Invalid lead status")
        lead.status = new_status
        return LeadRepository.save(lead)

    @staticmethod
    def convert_lead(lead):
        if lead.status == "converted":
            raise ValidationError("Lead already converted")
        lead.status = "converted"
        return LeadRepository.save(lead)

        lead.status = "converted"
        self.repo.save(lead)

        return lead