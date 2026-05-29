from .models import Activity, ActivityType


class ActivityRepository:

    @staticmethod
    def get_by_id(activity_id):
        return Activity.objects.filter(id=activity_id, is_deleted=False).first()

    @staticmethod
    def get_by_org(organization):
        return Activity.objects.filter(organization=organization, is_deleted=False)

    @staticmethod
    def list():
        return Activity.objects.filter(is_deleted=False)

    @staticmethod
    def create(**data):
        return Activity.objects.create(**data)

    @staticmethod
    def save(activity):
        activity.save()
        return activity
    
    @staticmethod
    def delete(activity):
        activity.is_deleted = True
        return ActivityRepository.save(activity)


class ActivityTypeRepository:

    @staticmethod
    def get_by_id(type_id):
        return ActivityType.objects.filter(id=type_id, is_deleted=False).first()

    @staticmethod
    def list():
        return ActivityType.objects.filter(is_deleted=False, is_active=True)

    @staticmethod
    def create(**data):
        return ActivityType.objects.create(**data)

    @staticmethod
    def save(activity_type):
        activity_type.save()
        return activity_type