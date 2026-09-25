from django.conf import settings
from django.db import models
from django.urls import reverse

from core.models import CodedModel, TimeStamped
from core.uploads import report_media
from core.validators import latitude_validators, longitude_validators


class EnvironmentalReport(CodedModel, TimeStamped):
    CODE_FIELD = "report_code"

    class Category(models.TextChoices):
        TREE_CUTTING = "tree_cutting", "🪓 قطع أشجار"
        FIRE = "fire", "🔥 حريق"
        ILLEGAL_HUNTING = "illegal_hunting", "🏹 صيد جائر"
        WASTE = "waste", "🗑️ نفايات"
        GREEN_AREA_DESTRUCTION = "green_area_destruction", "🏗️ تجريف مساحة خضراء"
        POLLUTION = "pollution", "💧 تلوث"
        WILDLIFE_HARM = "wildlife_harm", "🐦 اعتداء على الحياة البرية"
        TREE_DAMAGE = "tree_damage", "🌳 شجرة متضررة"
        OTHER = "other", "➕ أخرى"

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "تم الاستلام"
        UNDER_REVIEW = "under_review", "قيد المراجعة"
        VERIFIED = "verified", "تم التحقق"
        FORWARDED = "forwarded", "أُحيل للجهة المختصة"
        IN_PROGRESS = "in_progress", "قيد المتابعة"
        RESOLVED = "resolved", "تمت المعالجة"
        REJECTED = "rejected", "مرفوض"
        DUPLICATE = "duplicate", "مكرر"

    class Priority(models.TextChoices):
        LOW = "low", "منخفضة"
        NORMAL = "normal", "عادية"
        HIGH = "high", "عالية"
        URGENT = "urgent", "عاجلة"

    # simplified 3-stage view shown to citizens: 🟡 → 🔵 → 🟢
    PUBLIC_STAGE = {
        Status.SUBMITTED: 0,
        Status.UNDER_REVIEW: 1,
        Status.VERIFIED: 1,
        Status.FORWARDED: 1,
        Status.IN_PROGRESS: 1,
        Status.RESOLVED: 2,
    }

    report_code = models.CharField("رقم البلاغ", max_length=30, unique=True, blank=True)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="reports", verbose_name="المبلّغ")
    category = models.CharField("نوع البلاغ", max_length=30, choices=Category.choices, db_index=True)
    title = models.CharField("عنوان مختصر", max_length=150, blank=True)
    description = models.TextField("الوصف")
    latitude = models.DecimalField("خط العرض", max_digits=9, decimal_places=6, validators=latitude_validators)
    longitude = models.DecimalField("خط الطول", max_digits=9, decimal_places=6, validators=longitude_validators)
    address_description = models.CharField("وصف المكان", max_length=250, blank=True)
    city = models.CharField("المدينة", max_length=60, default="الموصل", db_index=True)
    status = models.CharField("الحالة", max_length=20, choices=Status.choices, default=Status.SUBMITTED, db_index=True)
    priority = models.CharField("الأولوية", max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_reports", verbose_name="مسند إلى")
    public_note = models.TextField("ملاحظة للمبلّغ", blank=True)
    internal_notes = models.TextField("ملاحظات داخلية", blank=True)
    hide_reporter_identity = models.BooleanField("إخفاء هوية المبلّغ", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "بلاغ بيئي"
        verbose_name_plural = "البلاغات البيئية"

    def build_code(self):
        return f"ENV-{2000 + self.pk}"

    def __str__(self):
        return f"{self.report_code} — {self.get_category_display()}"

    def get_absolute_url(self):
        return reverse("reports:detail", args=[self.report_code])

    @property
    def public_stage(self):
        return self.PUBLIC_STAGE.get(self.status, -1)


class EnvironmentalReportMedia(models.Model):
    report = models.ForeignKey(EnvironmentalReport, on_delete=models.CASCADE, related_name="media")
    file = models.ImageField("صورة", upload_to=report_media)
    media_type = models.CharField(max_length=10, default="image")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مرفق البلاغ"
        verbose_name_plural = "مرفقات البلاغ"
