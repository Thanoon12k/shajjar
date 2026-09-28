from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from core.models import CodedModel, TimeStamped
from core.uploads import request_image
from core.validators import latitude_validators, longitude_validators

MAX_TREES_PER_REQUEST = 500
MAX_IMAGES_PER_REQUEST = 5


class TreeRequest(CodedModel, TimeStamped):
    CODE_FIELD = "request_code"

    class LocationType(models.TextChoices):
        HOME = "home", "🏠 أمام البيت"
        SHOP = "shop", "🏪 أمام المحل"
        SCHOOL = "school", "🏫 مدرسة"
        UNIVERSITY = "university", "🎓 جامعة"
        HOSPITAL = "hospital", "🏥 مستشفى"
        ORCHARD = "orchard", "🌾 بستان"
        VILLAGE = "village", "🏘️ قرية"
        INSTITUTION = "institution", "🏢 مؤسسة"
        STREET = "street", "🛣️ شارع"
        MOSQUE = "mosque", "🕌 جامع"
        PUBLIC = "public", "🌳 مكان عام"
        OTHER = "other", "➕ أخرى"

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "تم إرسال الطلب"
        UNDER_REVIEW = "under_review", "قيد المراجعة"
        APPROVED = "approved", "تمت الموافقة"
        READY = "ready_for_distribution", "جاهز للاستلام"
        DISTRIBUTED = "distributed", "تم الاستلام"
        PLANTED = "planted", "تمت الزراعة"
        COMPLETED = "completed", "مكتمل"
        REJECTED = "rejected", "مرفوض"

    TIMELINE = [
        Status.SUBMITTED,
        Status.UNDER_REVIEW,
        Status.APPROVED,
        Status.READY,
        Status.DISTRIBUTED,
        Status.PLANTED,
    ]

    request_code = models.CharField("رقم الطلب", max_length=30, unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tree_requests", verbose_name="صاحب الطلب")
    location_type = models.CharField("مكان الزراعة", max_length=20, choices=LocationType.choices)
    requested_tree_count = models.PositiveIntegerField("عدد الأشجار المطلوب", validators=[MinValueValidator(1), MaxValueValidator(MAX_TREES_PER_REQUEST)])
    approved_tree_count = models.PositiveIntegerField("العدد الموافق عليه", null=True, blank=True, validators=[MaxValueValidator(MAX_TREES_PER_REQUEST)])
    preferred_species = models.ForeignKey("species.TreeSpecies", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="النوع المفضل")
    watering_commitment = models.BooleanField("الالتزام بالسقي", default=True)
    latitude = models.DecimalField("خط العرض", max_digits=9, decimal_places=6, validators=latitude_validators)
    longitude = models.DecimalField("خط الطول", max_digits=9, decimal_places=6, validators=longitude_validators)
    address_description = models.CharField("وصف العنوان", max_length=250)
    governorate = models.CharField("المحافظة", max_length=60, default="نينوى")
    city = models.CharField("المدينة / القضاء", max_length=60, default="الموصل", db_index=True)
    district = models.CharField("الحي", max_length=80, blank=True, db_index=True)
    contact_phone = models.CharField("رقم التواصل", max_length=20, blank=True)
    notes = models.TextField("ملاحظات", blank=True)
    status = models.CharField("الحالة", max_length=30, choices=Status.choices, default=Status.SUBMITTED, db_index=True)
    assigned_supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="supervised_requests", verbose_name="المشرف")
    distribution_date = models.DateField("موعد الاستلام", null=True, blank=True)
    public_note = models.TextField("ملاحظة لصاحب الطلب", blank=True)
    internal_notes = models.TextField("ملاحظات داخلية", blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "طلب شجرة"
        verbose_name_plural = "طلبات الأشجار"

    def build_code(self):
        return f"SH-{1000 + self.pk}"

    def __str__(self):
        return self.request_code or "طلب جديد"

    def get_absolute_url(self):
        return reverse("tree_requests:detail", args=[self.request_code])

    def timeline(self):
        """List of (label, state) where state is done/current/pending."""
        if self.status == self.Status.REJECTED:
            return [
                (self.Status.SUBMITTED.label, "done"),
                (self.Status.UNDER_REVIEW.label, "done"),
                (self.Status.REJECTED.label, "rejected"),
            ]
        current = self.Status.PLANTED if self.status == self.Status.COMPLETED else self.status
        idx = self.TIMELINE.index(current) if current in self.TIMELINE else 0
        steps = []
        for i, st in enumerate(self.TIMELINE):
            state = "done" if i < idx else "current" if i == idx else "pending"
            if self.status == self.Status.COMPLETED:
                state = "done"
            steps.append((st.label, state))
        return steps


class TreeRequestImage(models.Model):
    tree_request = models.ForeignKey(TreeRequest, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("صورة المكان", upload_to=request_image)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "صورة الطلب"
        verbose_name_plural = "صور الطلب"
