from django import forms

from .validators import validate_image_file


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.FileField):
    def __init__(self, *args, max_files=5, **kwargs):
        self.max_files = max_files
        kwargs.setdefault("widget", MultipleFileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "multiple": True}))
        kwargs.setdefault("required", False)
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else ([data] if data else [])
        if self.required and not files:
            raise forms.ValidationError("الرجاء إرفاق صورة واحدة على الأقل.")
        if len(files) > self.max_files:
            raise forms.ValidationError(f"الحد الأقصى {self.max_files} صور.")
        cleaned = [super(MultipleImageField, self).clean(f, initial) for f in files]
        for f in cleaned:
            validate_image_file(f)
        return cleaned


class LocationFieldsMixin:
    """Accept any precision from GPS/map picker and round to 6 decimal places."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, limit in (("latitude", 90), ("longitude", 180)):
            if name in self.fields:
                old = self.fields[name]
                self.fields[name] = forms.DecimalField(
                    required=old.required,
                    min_value=-limit,
                    max_value=limit,
                    widget=old.widget,
                    error_messages={"required": "حدد الموقع على الخريطة."},
                )

    def _clean_coord(self, name):
        value = self.cleaned_data.get(name)
        return round(value, 6) if value is not None else value

    def clean_latitude(self):
        return self._clean_coord("latitude")

    def clean_longitude(self):
        return self._clean_coord("longitude")
