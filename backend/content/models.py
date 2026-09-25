from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import TimeStamped
from core.uploads import article_image, contribution_qr


class ArticleCategory(models.Model):
    name = models.CharField("الاسم", max_length=80)
    slug = models.SlugField(unique=True, allow_unicode=True)
    icon = models.CharField("رمز", max_length=8, default="🌿")
    is_legal = models.BooleanField("قسم قانوني (اعرف القانون)", default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "تصنيف"
        verbose_name_plural = "تصنيفات المحتوى"

    def __str__(self):
        return self.name


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True, published_at__lte=timezone.now())


class ContentArticle(TimeStamped):
    title = models.CharField("العنوان", max_length=200)
    slug = models.SlugField(unique=True, allow_unicode=True, max_length=220)
    summary = models.CharField("الملخص", max_length=300, blank=True)
    body = models.TextField("المحتوى")
    cover_image = models.ImageField("صورة", upload_to=article_image, blank=True)
    category = models.ForeignKey(ArticleCategory, on_delete=models.PROTECT, related_name="articles", verbose_name="التصنيف")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="الكاتب")
    source_url = models.URLField("المصدر", blank=True)
    needs_legal_review = models.BooleanField("بحاجة لمراجعة قانونية رسمية", default=False)
    published_at = models.DateTimeField("تاريخ النشر", default=timezone.now)
    is_published = models.BooleanField("منشور", default=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "مقال"
        verbose_name_plural = "المقالات والتوعية"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("content:article", args=[self.slug])


class ContributionMethod(models.Model):
    name = models.CharField("الوسيلة", max_length=100)
    description = models.TextField("الوصف", blank=True)
    account_information = models.CharField("معلومات الحساب", max_length=200, blank=True)
    qr_image = models.ImageField("رمز QR", upload_to=contribution_qr, blank=True)
    instructions = models.TextField("التعليمات", blank=True)
    is_active = models.BooleanField("فعّال", default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "وسيلة مساهمة"
        verbose_name_plural = "وسائل المساهمة"

    def __str__(self):
        return self.name


class ContributionGoal(models.Model):
    """«كلفة زراعة شجرة / دعم حملة / دعم منظومة ري» — informational cards only."""

    icon = models.CharField(max_length=8, default="🌱")
    title = models.CharField("العنوان", max_length=100)
    description = models.CharField("الوصف", max_length=250, blank=True)
    amount_iqd = models.PositiveIntegerField("المبلغ التقريبي (د.ع)", null=True, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "باب مساهمة"
        verbose_name_plural = "أبواب المساهمة"

    def __str__(self):
        return self.title
