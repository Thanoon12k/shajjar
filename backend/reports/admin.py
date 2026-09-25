from django.contrib import admin
from django.utils.html import format_html

from core.admin import AuditedAdmin

from .models import EnvironmentalReport, EnvironmentalReportMedia


class MediaInline(admin.TabularInline):
    model = EnvironmentalReportMedia
    extra = 0
    readonly_fields = ["preview"]

    @admin.display(description="معاينة")
    def preview(self, obj):
        return format_html('<img src="{}" style="height:80px;border-radius:8px">', obj.file.url) if obj.file else "-"


@admin.register(EnvironmentalReport)
class ReportAdmin(AuditedAdmin):
    owner_field = "reporter"
    notify_type = "report"
    list_display = ["report_code", "category", "priority", "status", "city", "address_description", "created_at"]
    list_filter = ["status", "category", "priority", "city"]
    search_fields = ["report_code", "title", "description", "address_description"]
    readonly_fields = ["report_code", "created_at", "updated_at", "map_link"]
    autocomplete_fields = ["reporter", "assigned_to"]
    inlines = [MediaInline]
    date_hierarchy = "created_at"
    actions = ["verify", "in_progress", "resolve", "reject"]

    @admin.display(description="الخريطة")
    def map_link(self, obj):
        return format_html('<a target="_blank" href="https://www.openstreetmap.org/?mlat={0}&mlon={1}#map=18/{0}/{1}">📍 فتح الموقع</a>', obj.latitude, obj.longitude)

    @admin.action(description="🔎 تم التحقق")
    def verify(self, request, qs):
        self.set_status(request, qs, EnvironmentalReport.Status.VERIFIED, "تم التحقق")

    @admin.action(description="🔵 قيد المتابعة")
    def in_progress(self, request, qs):
        self.set_status(request, qs, EnvironmentalReport.Status.IN_PROGRESS, "قيد المتابعة")

    @admin.action(description="🟢 تمت المعالجة")
    def resolve(self, request, qs):
        self.set_status(request, qs, EnvironmentalReport.Status.RESOLVED, "تمت المعالجة")

    @admin.action(description="❌ رفض")
    def reject(self, request, qs):
        self.set_status(request, qs, EnvironmentalReport.Status.REJECTED, "مرفوض")
