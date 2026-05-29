from .models import Contact


class ContactRepository:

    @staticmethod
    def get_by_id(contact_id):
        return Contact.objects.filter(id=contact_id, is_deleted=False).first()

    @staticmethod
    def get_by_org(organization):
        return Contact.objects.filter(organization=organization, is_deleted=False)

    @staticmethod
    def get_by_company(company):
        return Contact.objects.filter(company=company, is_deleted=False)

    @staticmethod
    def list():
        return Contact.objects.filter(is_deleted=False)

    @staticmethod
    def create(**data):
        return Contact.objects.create(**data)

    @staticmethod
    def save(contact):
        contact.save()
        return contact
    
    @staticmethod
    def delete(contact):
        contact.is_deleted = True
        return ContactRepository.save(contact)