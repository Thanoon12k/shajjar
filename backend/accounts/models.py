from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from core.uploads import profile_image


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("البريد الإلكتروني مطلوب")
        user = self.model(email=self.normalize_email(email).lower(), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", User.Role.SUPER_ADMIN)
        return self._create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        CITIZEN = "citizen", "مواطن"
        VOLUNTEER = "volunteer", "متطوع"
        SUPERVISOR = "supervisor", "مشرف ميداني"
        ADMIN = "admin", "مدير"
        SUPER_ADMIN = "super_admin", "مدير عام"

    email = models.EmailField("البريد الإلكتروني", unique=True)
    phone_number = models.CharField("رقم الهاتف", max_length=20, blank=True)
    full_name = models.CharField("الاسم الكامل", max_length=150)
    profile_image = models.ImageField("الصورة الشخصية", upload_to=profile_image, blank=True)
    governorate = models.CharField("المحافظة", max_length=60, default="نينوى")
    city = models.CharField("المدينة", max_length=60, default="الموصل", db_index=True)
    district = models.CharField("الحي/المنطقة", max_length=80, blank=True, db_index=True)
    role = models.CharField("الدور", max_length=20, choices=Role.choices, default=Role.CITIZEN)
    is_verified = models.BooleanField("موثّق", default=False)
    is_active = models.BooleanField("فعّال", default=True)
    is_staff = models.BooleanField("من فريق الإدارة", default=False)
    date_joined = models.DateTimeField("تاريخ الانضمام", default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"

    def __str__(self):
        return self.full_name or self.email

    @property
    def first_name(self):
        return (self.full_name or "").split(" ")[0]

    @property
    def is_team(self):
        return self.is_staff or self.role in {self.Role.SUPERVISOR, self.Role.ADMIN, self.Role.SUPER_ADMIN}
