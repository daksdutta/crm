from .repositories import ActivityRepository, ActivityTypeRepository
from django.db import transaction


class ActivityService:

    @staticmethod
    @transaction.atomic
    def create_activity(data, user):
        data["owner"] = user
        data["organization"] = user.organization
        return ActivityRepository.create(**data)

    @staticmethod
    @transaction.atomic
    def update_activity(activity, data):
        for field, value in data.items():
            if field not in ["id", "organization", "created_at", "updated_at", "is_deleted"]:
                setattr(activity, field, value)
        return ActivityRepository.save(activity)

    @staticmethod
    def delete_activity(activity):
        return ActivityRepository.delete(activity)
    
    @staticmethod
    @transaction.atomic
    def complete_activity(activity):
        activity.status = "completed"
        return ActivityRepository.save(activity)
    
    @staticmethod
    @transaction.atomic
    def cancel_activity(activity):
        activity.status = "cancelled"
        return ActivityRepository.save(activity)


class ActivityTypeService:

    @staticmethod
    @transaction.atomic
    def create_type(data):
        return ActivityTypeRepository.create(**data)

    @staticmethod
    @transaction.atomic
    def update_type(activity_type, data):
        for field, value in data.items():
            if field not in ["id", "created_at", "updated_at", "is_deleted"]:
                setattr(activity_type, field, value)
        return ActivityTypeRepository.save(activity_type)
    
    @staticmethod
    def delete_type(activity_type):
        activity_type.is_deleted = True
        return ActivityTypeRepository.save(activity_type)

    def delete_type(self, activity_type):

        activity_type.is_deleted = True
        self.repo.save(activity_type)

        return activity_type