from django.urls import path

from user.views import CreateUserView, ManageUserView, ObtainTokenView

app_name = "user"

urlpatterns = [
    path("create", CreateUserView.as_view(), name="create"),
    path("token/", ObtainTokenView.as_view(), name="token"),
    path("me/", ManageUserView.as_view(), name="me"),
]
