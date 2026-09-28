from django.conf import settings
from django.db import models
from django.urls import reverse

from core.models import CodedModel, TimeStamped
from core.uploads import site_image
from core.validators import latitude_validators, longitude_validators


class PlantingSite(TimeStamped):
    class Kind(models.TextChoices):
        FOREST = "forest", "غابة / مشروع تشجير"
        STREET = "street", "شارع"
        NEIGHBORHOOD = "neighborhood", "حي سكني"
        ORCHARD = "orchard", "بستان"
        SCHOOL = "school", "مدرسة / جامعة"
        HOSPITAL = "hospital", "مستشفى"
        INSTITUTION = "institution", "مؤسسة / دائرة"
        VILLAGE = "village", "قرية"
        PUBLIC = "public", "مكان عام"

    class Status(models.TextChoices):
        ACTIVE = "active", "فعّال"
        NEEDS_ATTENTION = "needs_attention", "يحتاج متابعة"
        COMPLETED = "completed", "مكتمل"
        INACTIVE = "inactive", "متوقف"

    name = models.CharField("اسم الموقع", max_length=150)
    kind = models.CharField("نوع الموقع", max_length=20, choices=Kind.choices, default=Kind.STREET)
    governorate = models.CharField("المحافظة", max_length=60, default="نينوى")
    city = models.CharField("المدينة / القضاء", max_length=60, default="الموصل", db_index=True)
    district = models.CharField("الحي / المنطقة", max_length=80, blank=True, db_index=True)
    latitude = models.DecimalField("خط العرض", max_digits=9, decimal_places=6, validators=latitude_validators)
    longitude = models.DecimalField("خط الطول", max_digits=9, decimal_places=6, validators=longitude_validators)
    description = models.TextField("الوصف", blank=True)
    organization = models.CharField("الجهة المنفذة", max_length=150, blank=True)
    watering_entity = models.CharField("المسؤول عن السقي", max_length=150, blank=True)
    planting_date = models.DateField("تاريخ الزراعة", null=True, blank=True, db_index=True)
    species = models.ManyToManyField("species.TreeSpecies", blank=True, related_name="sites", verbose_name="الأنواع المزروعة")
    total_trees = models.PositiveIntegerField("عدد الأشجار المزروعة", default=0)
    alive_trees = models.PositiveIntegerField("الأشجار الحية", default=0)
    damaged_trees = models.PositiveIntegerField("الأشجار المتضررة", default=0)
    dead_trees = models.PositiveIntegerField("الأشجار الميتة", default=0)
    cover_image = models.ImageField("صورة الغلاف", upload_to=site_image, blank=True)
    before_image = models.ImageField("صورة قبل", upload_to=site_image, blank=True)
    after_image = models.ImageField("صورة بعد", upload_to=site_image, blank=True)
    source_url = models.URLField("رابط التوثيق (منشور)", blank=True)
    status = models.CharField("الحالة", max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    is_featured = models.BooleanField("مميز في الرئيسية", default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="أنشأه")

    class Meta:
        ordering = ["-is_featured", "-planting_date"]
        verbose_name = "موقع تشجير"
        verbose_name_plural = "مواقع التشجير"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("planting:site", args=[self.pk])

    @property
    def survival_rate(self):
        if not self.total_trees:
            return None
        return round(self.alive_trees / self.total_trees * 100, 1)

    @property
    def health(self):
        """good / attention / damaged — drives the map marker colour."""
        if self.kind == self.Kind.FOREST and self.status != self.Status.NEEDS_ATTENTION:
            base = "forest"
        else:
            base = None
        rate = self.survival_rate
        if self.status == self.Status.NEEDS_ATTENTION:
            return "attention"
        if rate is not None and rate < 60:
            return "damaged"
        if rate is not None and rate < 85:
            return "attention"
        return base or "good"


class PlantingBatch(CodedModel, TimeStamped):
    CODE_FIELD = "batch_code"

    batch_code = models.CharField("رمز الدفعة", max_length=30, unique=True, blank=True)
    planting_site = models.ForeignKey(PlantingSite, on_delete=models.CASCADE, related_name="batches", verbose_name="الموقع")
    species = models.ForeignKey("species.TreeSpecies", on_delete=models.PROTECT, related_name="batches", verbose_name="النوع")
    quantity = models.PositiveIntegerField("العدد")
    planting_date = models.DateField("تاريخ الزراعة", null=True, blank=True, db_index=True)
    responsible_entity = models.CharField("الجهة المسؤولة", max_length=150, blank=True)
    watering_entity = models.CharField("المسؤول عن السقي", max_length=150, blank=True)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta:
        ordering = ["-planting_date"]
        verbose_name = "دفعة زراعة"
        verbose_name_plural = "دفعات الزراعة"

    def build_code(self):
        year = (self.planting_date or self.created_at).year
        return f"BAT-{year}-{self.pk:06d}"

    def __str__(self):
        return f"{self.batch_code} — {self.species} × {self.quantity}"
