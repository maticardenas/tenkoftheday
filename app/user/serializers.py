from typing import TYPE_CHECKING, Dict, Any

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

if TYPE_CHECKING:
    from core.models import User


class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the users object """

    class Meta:
        model = get_user_model()
        fields = ("email", "password", "name")
        extra_kwargs = {
            "password": {
                "write_only": True, # We only want password to create new objects, not retrieving
                "min_length": 5,
                "style": {"input_type": "password"} # Don't show password while writing it
            }
        }

    # We need it because we need to call the create method of the model as
    # we need to store the password as hash.
    def create(self, validated_data: Dict[str, Any]) -> "User":
        """ Creates and returns a new user """
        return get_user_model().objects.create_user(**validated_data)

    # Also this one for making sure the set_password function is used for the password
    def update(self, instance: "User", validated_data: Dict[str, Any]) -> "User":
        """ Updates the user  """
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """ Serializer for the user authentication object """
    email = serializers.CharField()
    password = serializers.CharField(
        style = {"input_type": "password"},
        trim_whitespace=False
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """ Validate and authenticate the user """
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password
        )

        if not user:
            msg = ("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authentication")

        attrs["user"] = user
        return attrs



