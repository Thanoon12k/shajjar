from django import forms

from core.forms import LocationFieldsMixin
from core.validators import validate_image_file

from .models import Health, TreeUpdate


class TreeUpdateForm(LocationFieldsMixin, forms.ModelForm):
    health_status = forms.ChoiceField(
        label="حالة الشجرة",
        choices=[
            (Health.EXCELLENT, "💚 ممتازة"),
            (Health.GOOD, "✅ جيدة"),
            (Health.NEEDS_CARE, "🟡 تحتاج رعاية"),
            (Health.DAMAGED, "🟠 متضررة"),
            (Health.DEAD, "🔴 ماتت"),
        ],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = TreeUpdate
        fields = ["photo", "height_cm", "health_status", "notes", "latitude", "longitude"]
        widgets = {
            "photo": forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "capture": "environment"}),
            "height_cm": forms.NumberInput(attrs={"min": 0, "max": 3000, "placeholder": "مثلاً 150"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "latitude": forms.HiddenInput,
            "longitude": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["photo"].required = True

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo:
            validate_image_file(photo)
        return photo
