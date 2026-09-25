from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone

from core.models import TimeStamped
from core.uploads import campaign_image
from core.validators import latitude_validators, longitude_validators


class Campaign(TimeStamped):
    class Status(models.TextChoices):
        DRAFT = "draft", "مسودة"
        PUBLISHED = "published", "التسجيل مفتوح"
        REGISTRATION_CLOSED = "registration_closed", "التسجيل مغلق"
        ACTIVE = "active", "جارية الآن"
        COMPLETED = "completed", "منجزة"
        CANCELLED = "cancelled", "ملغاة"

    title = models.CharField("عنوان الحملة", max_length=150)
    description = models.TextField("الوصف")
    cover_image = models.ImageField("صورة الغلاف", upload_to=campaign_image, blank=True)
    location_name = models.CharField("المكان", max_length=150)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=latitude_validators)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=longitude_validators)
    start_date = models.DateTimeField("موعد البدء", db_index=True)
    end_date = models.DateTimeField("موعد الانتهاء", null=True, blank=True)
    registration_deadline = models.DateTimeField("آخر موعد للتسجيل", null=True, blank=True)
    target_tree_count = models.PositiveIntegerField("الهدف (أشجار)", default=0)
    volunteers_needed = models.PositiveIntegerField("المتطوعون المطلوبون", default=0)
    organization = models.CharField("الجهة المنظمة", max_length=150, blank=True)
    status = models.CharField("الحالة", max_length=25, choices=Status.choices, default=Status.DRAFT, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "حملة"
        verbose_name_plural = "الحملات"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("campaigns:detail", args=[self.pk])

    @property
    def active_participants(self):
        return self.participants.exclude(status=CampaignParticipant.Status.CANCELLED)

    @property
    def registration_open(self):
        if self.status != self.Status.PUBLISHED:
            return False
        deadline = self.registration_deadline or self.start_date
        if deadline and timezone.now() > deadline:
            return False
        if self.volunteers_needed and self.active_participants.count() >= self.volunteers_needed:
            return False
        return True

    @property
    def trees_planted(self):
        return self.participants.aggregate(s=Sum("trees_planted"))["s"] or 0


class CampaignParticipant(models.Model):
    class Status(models.TextChoices):
        REGISTERED = "registered", "مسجّل"
        APPROVED = "approved", "مقبول"
        ATTENDED = "attended", "حضر"
        ABSENT = "absent", "غائب"
        COMPLETED = "completed", "أنجز"
        CANCELLED = "cancelled", "ألغى المشاركة"

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="participants", verbose_name="الحملة")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="participations", verbose_name="المتطوع")
    status = models.CharField("الحالة", max_length=15, choices=Status.choices, default=Status.REGISTERED)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    volunteer_hours = models.DecimalField("ساعات التطوع", max_digits=5, decimal_places=1, default=0)
    trees_planted = models.PositiveIntegerField("أشجار زرعها", default=0)
    notes = models.TextField(blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مشارك"
        verbose_name_plural = "المشاركون"
        constraints = [models.UniqueConstraint(fields=["campaign", "user"], name="unique_campaign_participant")]

    def __str__(self):
        return f"{self.user} @ {self.campaign}"
