from django.conf import settings
from django.db import models


class TimeStamped(models.Model):
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("آخر تعديل", auto_now=True)

    class Meta:
        abstract = True


class CodedModel(models.Model):
    """Assigns a human-readable code (e.g. SH-1048) right after the first save."""

    CODE_FIELD = "code"
    CODE_FORMAT = "{id}"

    class Meta:
        abstract = True

    def build_code(self):
        return self.CODE_FORMAT.format(id=self.pk, year=self.created_at.year if hasattr(self, "created_at") and self.created_at else "")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not getattr(self, self.CODE_FIELD):
            code = self.build_code()
            setattr(self, self.CODE_FIELD, code)
            type(self).objects.filter(pk=self.pk).update(**{self.CODE_FIELD: code})


class Notification(models.Model):
    class Type(models.TextChoices):
        GENERAL = "general", "عام"
        REQUEST = "request", "طلب شجرة"
        TREE = "tree", "متابعة شجرة"
        REPORT = "report", "بلاغ بيئي"
        CAMPAIGN = "campaign", "حملة"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications", verbose_name="المستخدم")
    title = models.CharField("العنوان", max_length=200)
    body = models.TextField("النص", blank=True)
    type = models.CharField("النوع", max_length=20, choices=Type.choices, default=Type.GENERAL)
    link = models.CharField("الرابط", max_length=300, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.PositiveBigIntegerField(null=True, blank=True)
    is_read = models.BooleanField("مقروء", default=False)
    created_at = models.DateTimeField("التاريخ", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "إشعار"
        verbose_name_plural = "الإشعارات"

    def __str__(self):
        return self.title


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="المنفّذ")
    action = models.CharField("الإجراء", max_length=100)
    object_type = models.CharField("نوع الكائن", max_length=100)
    object_id = models.CharField("المعرف", max_length=50)
    metadata = models.JSONField("تفاصيل", default=dict, blank=True)
    created_at = models.DateTimeField("التاريخ", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "سجل تدقيق"
        verbose_name_plural = "سجل التدقيق"

    def __str__(self):
        return f"{self.action} — {self.object_type}#{self.object_id}"
