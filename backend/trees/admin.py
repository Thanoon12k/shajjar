from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from core.services import audit

from .models import Health, Tree, TreeUpdate


class UpdateInline(admin.TabularInline):
    model = TreeUpdate
    extra = 0
    fields = ["created_at", "photo", "height_cm", "health_status", "notes", "verified"]
    readonly_fields = []


@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    list_display = ["tree_code", "species", "place", "owner", "planting_date", "height_cm", "health_status", "status", "last_update_at", "qr"]
    list_filter = ["health_status", "status", "species", "site__city"]
    search_fields = ["tree_code", "owner__full_name", "owner__email", "location_label", "site__name"]
    readonly_fields = ["tree_code", "qr_identifier", "last_update_at", "qr"]
    autocomplete_fields = ["species", "site", "owner", "caretaker", "batch", "request"]
    inlines = [UpdateInline]
    actions = ["mark_dead", "mark_needs_care"]
    date_hierarchy = "planting_date"

    @admin.display(description="QR")
    def qr(self, obj):
        if not obj.pk:
            return "-"
        return format_html('<a href="{}?download=1">⬇️ QR</a>', f"/trees/{obj.tree_code}/qr.svg")

    @admin.action(description="🔴 تعليم كميتة")
    def mark_dead(self, request, queryset):
        for t in queryset:
            t.status, t.health_status = Tree.Status.DEAD, Health.DEAD
            t.save()
            audit(request.user, "tree_marked_dead", t)
        self.message_user(request, "تم التحديث")

    @admin.action(description="🟡 تحتاج رعاية")
    def mark_needs_care(self, request, queryset):
        queryset.update(health_status=Health.NEEDS_CARE, updated_at=timezone.now())


@admin.register(TreeUpdate)
class TreeUpdateAdmin(admin.ModelAdmin):
    list_display = ["tree", "user", "health_status", "height_cm", "verified", "created_at", "thumb"]
    list_filter = ["verified", "health_status"]
    search_fields = ["tree__tree_code", "user__full_name"]
    autocomplete_fields = ["tree", "user", "verified_by"]
    actions = ["verify"]

    @admin.display(description="صورة")
    def thumb(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height:48px;border-radius:6px">', obj.photo.url)
        return "-"

    @admin.action(description="✅ توثيق التحديثات")
    def verify(self, request, queryset):
        n = queryset.filter(verified=False).update(verified=True, verified_by=request.user)
        self.message_user(request, f"تم توثيق {n} تحديث")
