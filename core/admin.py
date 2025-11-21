from django.contrib import admin
from .models import User
# Register your models here.
"""
Django Admin configuration for Core models
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User



class UserProfileInline(admin.StackedInline):
    """Inline profile editing in User admin"""
    model = User
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    """Extended User admin with profile"""
    inlines = (UserProfileInline,)

    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'profile__role']

    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'N/A'

    get_role.short_description = 'Role'


# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile"""
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
