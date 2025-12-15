from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValitionError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class BaseUserSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        user = self.context.get("user", self.instance)
        password = attrs.get("password")
        if password:
            try:
                validate_password(password, user)
            except DjangoValitionError as error:

                raise serializers.ValidationError(
                    {"password": error.error_list}
                )
            except KeyError:
                pass
        return attrs

    class Meta:
        model = get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs = {"password": {"write_only": True}}


class CreateUserSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        pass

    def validate(self, attrs):
        user = get_user_model()(name=attrs["name"], email=attrs["email"])
        self.context["user"] = user
        return super().validate(attrs)

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class UpdateUserSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        read_only_fields = ["email"]

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class TokenSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]
        user = authenticate(
            self.context.get("request"), username=email, password=password
        )

        if not user:
            raise serializers.ValidationError(
                _(
                    "No user found with this email and password",
                ),
                code="authorization",
            )
        attrs["user"] = user
        return attrs
