from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import Ingredient, Recipe, Tag, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["name", "email"]
    ordering = ["id"]
    fieldsets = (
        (None, {"fields": ("email", "password", "name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    readonly_fields = ["last_login"]


admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
