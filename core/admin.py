from django.contrib import admin
from django.contrib.auth import get_permission_codename
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ngettext
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

from .models import *


class UserAdminConfig(UserAdmin):
    model = User
    search_fields = ('full_name', 'first_name', 'last_name')
    list_filter = ('gender', 'has_admin_permit', 'is_active', 'is_staff')
    ordering = ('-start_date',)
    list_display = ('full_name', 'first_name', 'last_name', 'has_admin_permit', 'is_active', 'is_staff')
    fieldsets = (
        ('Kullanıcı Bilgileri', {'fields': ('full_name', 'password')}),
        ('Genel Bilgi',
         {'fields': ('first_name', 'last_name', 'father', 'mother', 'gender', 'birth_date', 'about', 'avatar')}),
        ('İzinler', {'fields': ('groups', 'user_permissions', 'is_staff', 'is_active', 'has_admin_permit')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'full_name', 'password1', 'password2', 'first_name', 'last_name', 'father', 'mother', 'gender',
                'birth_date', 'about', 'is_active')}
         ),
    )


class MediaAdminConfig(admin.ModelAdmin):
    search_fields = ('user_tag', 'alt_text')
    list_filter = ('user_tag', 'is_only_my_family', 'created_at', 'updated_at')
    ordering = ('-updated_at',)
    list_display = ('get_user_tag', 'alt_text', 'is_only_my_family', 'created_at')
    fieldsets = (
        ('İzinler', {'fields': ('user_tag', 'is_only_my_family')}),
        ('Media Bilgileri', {'fields': ('img_url', 'alt_text')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_tag', 'img_url')}
         ),
    )


class RequestedUserPermitLogAdminConfig(admin.ModelAdmin):
    search_fields = ('user__full_name', 'status')
    list_filter = ('user', 'status', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_display = ('user', 'status', 'created_at', 'updated_at')
    actions = ['make_published']

    @admin.action(permissions=['permit'], description='Seçili kullanacılara izin Ver')
    def make_published(self, request, queryset):
        for model in queryset:
            User.objects.filter(pk=model.user.pk).update(is_active=True, has_admin_permit=True)
        updated = queryset.update(status=False)
        self.message_user(request, '%d Kullanıcı için izin işlemi başarılı.' % updated, messages.SUCCESS)

    @staticmethod
    def has_permit_permission(request):
        if request.user.is_superuser:
            return True
        return False


class CurrentGroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["name"]}


admin.site.register(User, UserAdminConfig)
admin.site.register(LastName)
admin.site.register(Media, MediaAdminConfig)
admin.site.register(RequestedUserPermitLog, RequestedUserPermitLogAdminConfig)
