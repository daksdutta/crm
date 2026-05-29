from .repositories import ContactRepository
from django.db import transaction


class ContactService:

    @staticmethod
    @transaction.atomic
    def create_contact(data, user):
        data["owner"] = user
        data["organization"] = user.organization
        return ContactRepository.create(**data)

    @staticmethod
    @transaction.atomic
    def update_contact(contact, data):
        for field, value in data.items():
            if field not in ["id", "organization", "created_at", "updated_at", "is_deleted"]:
                setattr(contact, field, value)
        return ContactRepository.save(contact)

    @staticmethod
    def delete_contact(contact):
        return ContactRepository.delete(contact)