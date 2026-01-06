from django.contrib import admin

from .models import (
    AIEmailDraft,
    CallScript,
    ContactPersonaMatch,
    DealInsight,
    ObjectionResponse,
    PersonaProfile,
    SalesCoachAdvice,
    WinLossAnalysis,
)


@admin.register(AIEmailDraft)
class AIEmailDraftAdmin(admin.ModelAdmin):
    list_display = ['subject', 'user', 'email_type', 'tone', 'was_used', 'user_rating', 'created_at']
    list_filter = ['email_type', 'tone', 'was_used']
    search_fields = ['subject', 'user__username']


@admin.register(SalesCoachAdvice)
class SalesCoachAdviceAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'advice_type', 'priority', 'is_completed', 'was_helpful', 'created_at']
    list_filter = ['advice_type', 'priority', 'is_completed', 'is_dismissed']
    search_fields = ['title', 'advice']


@admin.register(ObjectionResponse)
class ObjectionResponseAdmin(admin.ModelAdmin):
    list_display = ['objection', 'category', 'times_used', 'success_rate', 'is_system']
    list_filter = ['category', 'is_system']
    search_fields = ['objection', 'best_response']


@admin.register(CallScript)
class CallScriptAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'script_type', 'times_used', 'success_rate', 'is_template']
    list_filter = ['script_type', 'is_template', 'is_active']
    search_fields = ['name']


@admin.register(DealInsight)
class DealInsightAdmin(admin.ModelAdmin):
    list_display = ['title', 'opportunity', 'insight_type', 'confidence', 'impact_score', 'is_acknowledged']
    list_filter = ['insight_type', 'is_acknowledged', 'is_actioned']
    search_fields = ['title', 'insight']


@admin.register(WinLossAnalysis)
class WinLossAnalysisAdmin(admin.ModelAdmin):
    list_display = ['opportunity', 'outcome', 'deal_duration_days', 'stakeholders_involved', 'created_at']
    list_filter = ['outcome']
    search_fields = ['opportunity__name']


@admin.register(PersonaProfile)
class PersonaProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'contacts_matched', 'deals_won', 'deals_lost', 'win_rate', 'is_system']
    list_filter = ['is_system']
    search_fields = ['name', 'description']


@admin.register(ContactPersonaMatch)
class ContactPersonaMatchAdmin(admin.ModelAdmin):
    list_display = ['contact', 'persona', 'confidence_score', 'created_at']
    list_filter = ['persona']
    search_fields = ['contact__email', 'contact__first_name']
