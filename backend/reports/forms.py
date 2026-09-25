from django import forms

from core.forms import LocationFieldsMixin, MultipleImageField

from .models import EnvironmentalReport


class ReportForm(LocationFieldsMixin, forms.ModelForm):
    photos = MultipleImageField(label="📸 صور (حتى 5)", max_files=5)

    class Meta:
        model = EnvironmentalReport
        fields = ["category", "title", "description", "latitude", "longitude", "address_description", "city", "hide_reporter_identity"]
        widgets = {
            "category": forms.RadioSelect,
            "latitude": forms.HiddenInput,
            "longitude": forms.HiddenInput,
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "شنو صار؟ متى؟ هل التجاوز مستمر؟"}),
        }

    def clean_description(self):
        text = self.cleaned_data["description"].strip()
        if len(text) < 15:
            raise forms.ValidationError("اكتب وصفاً أوضح (15 حرفاً على الأقل) حتى نكدر نتابع البلاغ.")
        return text
