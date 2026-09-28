import os

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_BYTES = 8 * 1024 * 1024

latitude_validators = [MinValueValidator(-90), MaxValueValidator(90)]
longitude_validators = [MinValueValidator(-180), MaxValueValidator(180)]


def validate_image_file(f):
    ext = os.path.splitext(f.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("نوع الملف غير مدعوم. المسموح: JPG, PNG, WEBP.")
    if f.size and f.size > MAX_IMAGE_BYTES:
        raise ValidationError("حجم الصورة كبير، الحد الأقصى 8 ميغابايت.")
    try:
        from PIL import Image

        pos = f.tell() if hasattr(f, "tell") else 0
        Image.open(f).verify()
        f.seek(pos)
    except Exception as exc:  # noqa: BLE001
        raise ValidationError("الملف ليس صورة صالحة.") from exc
