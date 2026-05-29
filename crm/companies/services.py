from .repositories import CompanyRepository
from django.db import transaction


class CompanyService:

    @staticmethod
    @transaction.atomic
    def create_company(data, user):
        data["owner"] = user
        data["organization"] = user.organization
        return CompanyRepository.create(**data)
    
    @staticmethod
    @transaction.atomic
    def update_company(company, data):
        for field, value in data.items():
            if field not in ["id", "organization", "created_at", "updated_at", "is_deleted"]:
                setattr(company, field, value)
        return CompanyRepository.save(company)

    @staticmethod
    def delete_company(company):
        return CompanyRepository.delete(company)
