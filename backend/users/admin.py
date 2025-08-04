from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as Admin

from .models import Subscriptions

User = get_user_model()


class SubscriptionsInline(admin.TabularInline):
    model = Subscriptions
    fk_name = 'user'
    extra = 1
    verbose_name = 'пописка'
    verbose_name_plural = 'подписки'


class UserAdmin(Admin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    list_display = (
        'username',
        'email',
    )
    search_fields = (
        'username',
        'email',
    )
    inlines = (SubscriptionsInline, )


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )


admin.site.register(User, UserAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
