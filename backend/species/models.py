from django.db import models

from core.models import TimeStamped
from core.uploads import species_image

LEVELS = [(1, "ضعيف"), (2, "مقبول"), (3, "متوسط"), (4, "جيد"), (5, "ممتاز")]


class TreeSpecies(TimeStamped):
    class Water(models.IntegerChoices):
        LOW = 1, "قليل"
        MEDIUM = 2, "متوسط"
        HIGH = 3, "عالٍ"

    arabic_name = models.CharField("الاسم العربي", max_length=100)
    english_name = models.CharField("الاسم الإنكليزي", max_length=100, blank=True)
    scientific_name = models.CharField("الاسم العلمي", max_length=150, blank=True)
    emoji = models.CharField("رمز", max_length=8, default="🌳")
    description = models.TextField("الوصف", blank=True)
    image = models.ImageField("الصورة", upload_to=species_image, blank=True)
    heat_tolerance = models.PositiveSmallIntegerField("تحمل الحرارة", choices=LEVELS, default=3)
    drought_tolerance = models.PositiveSmallIntegerField("تحمل الجفاف", choices=LEVELS, default=3)
    water_requirement = models.PositiveSmallIntegerField("احتياج الماء", choices=Water.choices, default=Water.MEDIUM)
    growth_speed = models.PositiveSmallIntegerField("سرعة النمو", choices=LEVELS, default=3)
    shade_level = models.PositiveSmallIntegerField("الظل", choices=LEVELS, default=3)
    suitable_for_streets = models.BooleanField("مناسب للشوارع والأرصفة", default=False)
    suitable_for_gardens = models.BooleanField("مناسب للحدائق والبيوت", default=False)
    suitable_for_farms = models.BooleanField("مناسب للبساتين", default=False)
    suitable_for_public_spaces = models.BooleanField("مناسب للغابات والأماكن العامة", default=False)
    bird_friendly = models.BooleanField("مفيد للطيور", default=False)
    fruitful = models.BooleanField("مثمر", default=False)
    notes = models.TextField("ملاحظات", blank=True)
    is_active = models.BooleanField("فعّال", default=True)

    class Meta:
        ordering = ["arabic_name"]
        verbose_name = "نوع شجرة"
        verbose_name_plural = "أنواع الأشجار"

    def __str__(self):
        return self.arabic_name

    @property
    def placement_labels(self):
        labels = []
        if self.suitable_for_streets:
            labels.append("شوارع")
        if self.suitable_for_gardens:
            labels.append("بيوت وحدائق")
        if self.suitable_for_farms:
            labels.append("بساتين")
        if self.suitable_for_public_spaces:
            labels.append("غابات وأماكن عامة")
        return labels

    def match_score(self, place=None, sun=None, water=None):
        """Simple, transparent scoring used by «شنو أزرع؟» — returns 0..5 stars."""
        score = 0.0
        weight = 0.0
        if place:
            weight += 2
            score += 2 if getattr(self, f"suitable_for_{place}", False) else 0
        if sun == "strong":
            weight += 1.5
            score += 1.5 * self.heat_tolerance / 5
        elif sun == "partial":
            weight += 0.5
            score += 0.5
        if water == "low":
            weight += 1.5
            score += 1.5 * self.drought_tolerance / 5
        elif water == "medium":
            weight += 1
            score += 1 if self.water_requirement <= 2 else 0.5
        elif water == "high":
            weight += 0.5
            score += 0.5
        if not weight:
            return round((self.heat_tolerance + self.drought_tolerance) / 2)
        return max(1, round(score / weight * 5))
