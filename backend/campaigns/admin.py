from django.contrib import admin

from core.admin import AuditedAdmin

from .models import Campaign, CampaignParticipant


class ParticipantInline(admin.TabularInline):
    model = CampaignParticipant
    extra = 0
    autocomplete_fields = ["user"]
    fields = ["user", "status", "volunteer_hours", "trees_planted", "notes"]


@admin.register(Campaign)
class CampaignAdmin(AuditedAdmin):
    list_display = ["title", "location_name", "start_date", "target_tree_count", "volunteers_needed", "status"]
    list_filter = ["status"]
    search_fields = ["title", "location_name"]
    inlines = [ParticipantInline]
    actions = ["publish", "close", "complete"]

    @admin.action(description="📢 نشر الحملة")
    def publish(self, request, qs):
        self.set_status(request, qs, Campaign.Status.PUBLISHED, "تم النشر")

    @admin.action(description="🔒 إغلاق التسجيل")
    def close(self, request, qs):
        self.set_status(request, qs, Campaign.Status.REGISTRATION_CLOSED, "تم إغلاق التسجيل")

    @admin.action(description="🏁 منجزة")
    def complete(self, request, qs):
        self.set_status(request, qs, Campaign.Status.COMPLETED, "منجزة")


@admin.register(CampaignParticipant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ["user", "campaign", "status", "volunteer_hours", "trees_planted"]
    list_filter = ["status", "campaign"]
    list_editable = ["status", "volunteer_hours", "trees_planted"]
    search_fields = ["user__full_name", "user__email"]
    autocomplete_fields = ["user", "campaign"]
