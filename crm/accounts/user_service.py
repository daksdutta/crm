from accounts.models import User


class UserService:

    @staticmethod
    def create_user(data):

        password = data.pop("password")

        user = User(**data)
        user.set_password(password)
        user.save()

        return user


    @staticmethod
    def update_user(user, data):

        for field, value in data.items():
            setattr(user, field, value)

        user.save()

        return user


    @staticmethod
    def delete_user(user):

        user.is_deleted = True
        user.save()

        return user
