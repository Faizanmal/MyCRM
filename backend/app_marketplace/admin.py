from django.contrib import admin
from .models import (
    AppCategory, AppDeveloper, MarketplaceApp, AppVersion,
    AppInstallation, AppReview
)


@admin.register(AppCategory)
class AppCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(AppDeveloper)
class AppDeveloperAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'verification_status', 'total_apps', 'total_installs']
    list_filter = ['verification_status']
    search_fields = ['name', 'email']


@admin.register(MarketplaceApp)
class MarketplaceAppAdmin(admin.ModelAdmin):
    list_display = ['name', 'developer', 'app_type', 'status', 'pricing_type', 'install_count', 'rating_average']
    list_filter = ['status', 'app_type', 'pricing_type', 'is_featured', 'is_verified']
    search_fields = ['name', 'developer__name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ['app', 'version', 'is_approved', 'released_at']
    list_filter = ['is_approved']


@admin.register(AppInstallation)
class AppInstallationAdmin(admin.ModelAdmin):
    list_display = ['app', 'installed_by', 'status', 'installed_version', 'installed_at']
    list_filter = ['status']


@admin.register(AppReview)
class AppReviewAdmin(admin.ModelAdmin):
    list_display = ['app', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved']
