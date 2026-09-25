from django.contrib import admin

from .models import AuditLog, Notification


class AuditedAdmin(admin.ModelAdmin):
    """Records status changes to the audit log and notifies the owner."""

    status_field = "status"
    owner_field = None
    notify_type = "general"

    def save_model(self, request, obj, form, change):
        old = None
        if change and obj.pk:
            old = getattr(type(obj).objects.get(pk=obj.pk), self.status_field)
        super().save_model(request, obj, form, change)
        new = getattr(obj, self.status_field)
        if change and old != new:
            self.on_status_change(request, obj, old, new)

    def on_status_change(self, request, obj, old, new):
        from .services import audit, notify

        audit(request.user, f"status:{old}->{new}", obj)
        owner = getattr(obj, self.owner_field) if self.owner_field else None
        if owner:
            label = getattr(obj, f"get_{self.status_field}_display")()
            link = obj.get_absolute_url() if hasattr(obj, "get_absolute_url") else ""
            notify(owner, f"تحديث على {obj}: {label}", getattr(obj, "public_note", "") or "", type=self.notify_type, link=link, obj=obj)

    def set_status(self, request, queryset, new, message):
        n = 0
        for obj in queryset:
            old = getattr(obj, self.status_field)
            if old == new:
                continue
            setattr(obj, self.status_field, new)
            obj.save()
            self.on_status_change(request, obj, old, new)
            n += 1
        self.message_user(request, f"{message}: {n}")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "type", "is_read", "created_at"]
    list_filter = ["type", "is_read"]
    search_fields = ["title", "user__email", "user__full_name"]
    autocomplete_fields = ["user"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "actor", "action", "object_type", "object_id"]
    list_filter = ["object_type"]
    search_fields = ["action", "object_id", "actor__email"]
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
