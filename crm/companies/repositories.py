from .models import Company


class CompanyRepository:

    @staticmethod
    def get_by_id(company_id):
        return Company.objects.filter(id=company_id, is_deleted=False).first()

    @staticmethod
    def get_by_org(organization):
        return Company.objects.filter(organization=organization, is_deleted=False)
    
    @staticmethod
    def list_by_org(organization):
        return Company.objects.filter(organization=organization, is_deleted=False)

    @staticmethod
    def create(**data):
        return Company.objects.create(**data)

    @staticmethod
    def save(company):
        company.save()
        return company
    
    @staticmethod
    def delete(company):
        company.is_deleted = True
        return CompanyRepository.save(company)