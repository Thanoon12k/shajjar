import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import CodedModel, TimeStamped
from core.uploads import tree_update_image
from core.validators import latitude_validators, longitude_validators


class Health(models.TextChoices):
    EXCELLENT = "excellent", "ممتازة"
    GOOD = "good", "جيدة"
    NEEDS_CARE = "needs_care", "تحتاج رعاية"
    DAMAGED = "damaged", "متضررة"
    DEAD = "dead", "ماتت"


class Tree(CodedModel, TimeStamped):
    CODE_FIELD = "tree_code"

    class Status(models.TextChoices):
        ACTIVE = "active", "قائمة"
        DEAD = "dead", "ميتة"
        REPLACED = "replaced", "تم استبدالها"
        REMOVED = "removed", "أزيلت"

    tree_code = models.CharField("رمز الشجرة", max_length=30, unique=True, blank=True)
    qr_identifier = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    batch = models.ForeignKey("planting.PlantingBatch", null=True, blank=True, on_delete=models.SET_NULL, related_name="trees", verbose_name="الدفعة")
    site = models.ForeignKey("planting.PlantingSite", null=True, blank=True, on_delete=models.SET_NULL, related_name="trees", verbose_name="الموقع")
    request = models.ForeignKey("tree_requests.TreeRequest", null=True, blank=True, on_delete=models.SET_NULL, related_name="trees", verbose_name="الطلب")
    species = models.ForeignKey("species.TreeSpecies", on_delete=models.PROTECT, related_name="trees", verbose_name="النوع")
    nickname = models.CharField("اسم الشجرة (اختياري)", max_length=60, blank=True)
    latitude = models.DecimalField("خط العرض", max_digits=9, decimal_places=6, null=True, blank=True, validators=latitude_validators)
    longitude = models.DecimalField("خط الطول", max_digits=9, decimal_places=6, null=True, blank=True, validators=longitude_validators)
    location_label = models.CharField("الموقع (وصف)", max_length=150, blank=True)
    planting_date = models.DateField("تاريخ الزراعة", default=timezone.localdate, db_index=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="owned_trees", verbose_name="المستفيد")
    caretaker = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="cared_trees", verbose_name="الراعي")
    caretaker_name = models.CharField("اسم الراعي (إن لم يكن مسجلاً)", max_length=100, blank=True)
    height_cm = models.PositiveIntegerField("الطول (سم)", null=True, blank=True)
    health_status = models.CharField("الحالة الصحية", max_length=20, choices=Health.choices, default=Health.GOOD, db_index=True)
    status = models.CharField("الوضع", max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    last_update_at = models.DateTimeField("آخر متابعة", null=True, blank=True)

    class Meta:
        ordering = ["-planting_date", "-id"]
        verbose_name = "شجرة"
        verbose_name_plural = "الأشجار"

    def build_code(self):
        return f"SHJ-{self.pk:06d}"

    def __str__(self):
        return f"{self.tree_code} — {self.species}"

    def get_absolute_url(self):
        return reverse("trees:detail", args=[self.tree_code])

    @property
    def age_days(self):
        return (timezone.localdate() - self.planting_date).days

    @property
    def caretaker_display(self):
        if self.caretaker:
            return self.caretaker.full_name
        if self.caretaker_name:
            return self.caretaker_name
        return self.owner.full_name if self.owner else "فريق #شجّر"

    @property
    def place(self):
        if self.location_label:
            return self.location_label
        if self.site:
            return f"{self.site.district or self.site.name} – {self.site.city}"
        return "الموصل"

    @property
    def coords(self):
        if self.latitude is not None and self.longitude is not None:
            return self.latitude, self.longitude
        if self.site:
            return self.site.latitude, self.site.longitude
        return None

    def is_followed_by(self, user):
        return user.is_authenticated and (user.pk in (self.owner_id, self.caretaker_id) or user.is_team)


class TreeUpdate(models.Model):
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="updates", verbose_name="الشجرة")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="tree_updates", verbose_name="المرسل")
    photo = models.ImageField("الصورة", upload_to=tree_update_image, blank=True)
    height_cm = models.PositiveIntegerField("الطول التقريبي (سم)", null=True, blank=True)
    health_status = models.CharField("الحالة", max_length=20, choices=Health.choices)
    notes = models.TextField("ملاحظات", blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=latitude_validators)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=longitude_validators)
    is_planting_day = models.BooleanField("يوم الزراعة", default=False)
    verified = models.BooleanField("موثّق من الفريق", default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="verified_updates", verbose_name="وثّقه")
    created_at = models.DateTimeField("التاريخ", default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "تحديث متابعة"
        verbose_name_plural = "تحديثات المتابعة"

    def __str__(self):
        return f"{self.tree.tree_code} @ {self.created_at:%Y-%m-%d}"

    def apply_to_tree(self):
        tree = self.tree
        tree.health_status = self.health_status
        if self.height_cm:
            tree.height_cm = self.height_cm
        if self.health_status == Health.DEAD:
            tree.status = Tree.Status.DEAD
        tree.last_update_at = self.created_at
        tree.save(update_fields=["health_status", "height_cm", "status", "last_update_at", "updated_at"])
