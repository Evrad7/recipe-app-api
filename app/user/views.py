from rest_framework import permissions
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView

from user.serializers import (
    TokenSerializer,
    CreateUserSerializer,
    UpdateUserSerializer,
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


class CreateUserView(CreateAPIView):
    serializer_class = CreateUserSerializer


class ObtainTokenView(ObtainAuthToken):
    serializer_class = TokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(RetrieveUpdateAPIView):
    serializer_class = UpdateUserSerializer
    http_method_names = ["get", "patch"]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):  # type: ignore
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
