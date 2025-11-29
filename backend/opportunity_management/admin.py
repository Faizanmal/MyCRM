from django.contrib import admin
from .models import Opportunity


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'stage', 'amount', 'expected_close_date', 'created_at']
    list_filter = ['stage', 'expected_close_date', 'created_at']
    search_fields = ['name', 'description', 'owner__username']
    autocomplete_fields = ['owner', 'assigned_to']
    readonly_fields = ['created_at', 'updated_at']
