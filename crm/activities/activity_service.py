from activities.models import Activity


class ActivityService:

    @staticmethod
    def create_activity(data):

        activity = Activity.objects.create(**data)

        return activity


    @staticmethod
    def update_activity(activity, data):

        for field, value in data.items():
            setattr(activity, field, value)

        activity.save()

        return activity


    @staticmethod
    def delete_activity(activity):

        activity.is_deleted = True
        activity.save()

        return activity
