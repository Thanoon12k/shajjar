from django.contrib import admin
from django.utils.html import format_html

from core.admin import AuditedAdmin
from core.services import audit, notify
from trees.models import Tree

from .models import TreeRequest, TreeRequestImage


class ImageInline(admin.TabularInline):
    model = TreeRequestImage
    extra = 0
    readonly_fields = ["preview"]

    @admin.display(description="معاينة")
    def preview(self, obj):
        return format_html('<img src="{}" style="height:80px;border-radius:8px">', obj.image.url) if obj.image else "-"


@admin.register(TreeRequest)
class TreeRequestAdmin(AuditedAdmin):
    owner_field = "user"
    notify_type = "request"
    list_display = ["request_code", "user", "location_type", "requested_tree_count", "approved_tree_count", "district", "watering_commitment", "status", "created_at"]
    list_filter = ["status", "location_type", "watering_commitment", "city"]
    search_fields = ["request_code", "user__full_name", "user__email", "district", "address_description"]
    readonly_fields = ["request_code", "created_at", "updated_at", "map_link"]
    autocomplete_fields = ["user", "assigned_supervisor", "preferred_species"]
    inlines = [ImageInline]
    date_hierarchy = "created_at"
    actions = ["review", "approve", "reject", "ready", "distributed", "planted_register_trees"]

    @admin.display(description="الخريطة")
    def map_link(self, obj):
        return format_html('<a target="_blank" href="https://www.openstreetmap.org/?mlat={0}&mlon={1}#map=18/{0}/{1}">📍 فتح الموقع</a>', obj.latitude, obj.longitude)

    @admin.action(description="🔎 قيد المراجعة")
    def review(self, request, qs):
        self.set_status(request, qs, TreeRequest.Status.UNDER_REVIEW, "قيد المراجعة")

    @admin.action(description="✅ موافقة")
    def approve(self, request, qs):
        for r in qs.filter(approved_tree_count__isnull=True):
            r.approved_tree_count = r.requested_tree_count
            r.save(update_fields=["approved_tree_count"])
        self.set_status(request, qs, TreeRequest.Status.APPROVED, "تمت الموافقة")

    @admin.action(description="❌ رفض")
    def reject(self, request, qs):
        self.set_status(request, qs, TreeRequest.Status.REJECTED, "تم الرفض")

    @admin.action(description="📦 جاهز للاستلام")
    def ready(self, request, qs):
        self.set_status(request, qs, TreeRequest.Status.READY, "جاهز للاستلام")

    @admin.action(description="🚚 تم الاستلام")
    def distributed(self, request, qs):
        self.set_status(request, qs, TreeRequest.Status.DISTRIBUTED, "تم التوزيع")

    @admin.action(description="🌳 تمت الزراعة + تسجيل الأشجار (Tree ID)")
    def planted_register_trees(self, request, qs):
        created = 0
        for r in qs:
            if r.trees.exists():
                continue
            species = r.preferred_species
            if species is None:
                from species.models import TreeSpecies

                species = TreeSpecies.objects.filter(is_active=True).order_by("-drought_tolerance").first()
            if species is None:
                self.message_user(request, "أضف نوع شجرة واحد على الأقل أولاً", level="error")
                return
            for _ in range(r.approved_tree_count or r.requested_tree_count):
                Tree.objects.create(
                    species=species,
                    request=r,
                    owner=r.user,
                    latitude=r.latitude,
                    longitude=r.longitude,
                    location_label=f"{r.district or r.address_description} – {r.city}",
                )
                created += 1
            audit(request.user, "trees_registered", r, count=r.trees.count())
            notify(r.user, "🌳 أشجارك صار عدها ملف خاص!", "تكدر تتابعها وترفع صورها من صفحة «شجرتي».", type="tree", link="/trees/my/", obj=r)
        self.set_status(request, qs, TreeRequest.Status.PLANTED, "تمت الزراعة")
        self.message_user(request, f"تم تسجيل {created} شجرة")
