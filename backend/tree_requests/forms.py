from django import forms

from core.forms import LocationFieldsMixin, MultipleImageField
from species.models import TreeSpecies

from .models import MAX_IMAGES_PER_REQUEST, TreeRequest


class TreeRequestForm(LocationFieldsMixin, forms.ModelForm):
    watering_commitment = forms.TypedChoiceField(
        label="هل تستطيع الالتزام بالسقي؟",
        choices=[("yes", "✅ نعم، ألتزم بالسقي والرعاية"), ("no", "❌ لا، أحتاج مساعدة")],
        coerce=lambda v: v == "yes",
        widget=forms.RadioSelect,
        initial="yes",
    )
    photos = MultipleImageField(label="📸 صور المكان (حتى 5 صور)", max_files=MAX_IMAGES_PER_REQUEST)

    class Meta:
        model = TreeRequest
        fields = [
            "location_type",
            "requested_tree_count",
            "preferred_species",
            "latitude",
            "longitude",
            "address_description",
            "city",
            "district",
            "watering_commitment",
            "contact_phone",
            "notes",
        ]
        widgets = {
            "location_type": forms.RadioSelect,
            "latitude": forms.HiddenInput,
            "longitude": forms.HiddenInput,
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "مثلاً: الرصيف عرضه مترين، يوجد مصدر ماء قريب…"}),
            "address_description": forms.TextInput(attrs={"placeholder": "مثلاً: حي التعليم، قرب جامع…"}),
            "requested_tree_count": forms.NumberInput(attrs={"min": 1, "max": 500}),
            "contact_phone": forms.TextInput(attrs={"inputmode": "tel", "placeholder": "07xxxxxxxxx"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["preferred_species"].queryset = TreeSpecies.objects.filter(is_active=True)
        self.fields["preferred_species"].empty_label = "اترك الاختيار لفريق #شجّر"
