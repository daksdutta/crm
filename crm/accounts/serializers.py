from rest_framework import serializers
from .models import User, Department, DataAccessRequest
from django.contrib.auth.models import Group

class GroupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Group
        fields = ["id", "name"]


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = ["id", "email", "department", "phone", "password", "groups"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):

        groups = validated_data.pop("groups", [])
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        user.groups.set(groups)
        return user


class AccessRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataAccessRequest
        fields = "__all__"
        read_only_fields = ["requester", "status"]

    def validate(self, data):

        access_type = data.get("access_type")
        target_user = data.get("target_user")
        target_department = data.get("target_department")

        request_user = self.context["request"].user

        # user access validation
        if access_type == "user":

            if not target_user:
                raise serializers.ValidationError(
                    "target_user must be provided for user access request"
                )

            if target_user == request_user:
                raise serializers.ValidationError(
                    "You cannot request access to your own data"
                )

        # department access validation
        if access_type == "department":

            if not target_department:
                raise serializers.ValidationError(
                    "target_department must be provided for department access request"
                )

        return data