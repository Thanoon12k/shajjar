from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm

from .models import User


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="البريد الإلكتروني", widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}))
    password = forms.CharField(label="كلمة المرور", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))

    error_messages = {
        "invalid_login": "البريد الإلكتروني أو كلمة المرور غير صحيحة.",
        "inactive": "هذا الحساب غير فعّال.",
    }

    def clean_username(self):
        return self.cleaned_data["username"].lower()


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    password2 = forms.CharField(label="تأكيد كلمة المرور", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    wants_to_volunteer = forms.BooleanField(label="🤝 أرغب بالتطوع مع فريق #شجّر", required=False)

    class Meta:
        model = User
        fields = ["full_name", "email", "phone_number", "city", "district"]
        widgets = {"phone_number": forms.TextInput(attrs={"inputmode": "tel", "placeholder": "07xxxxxxxxx"})}

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("هذا البريد مسجّل مسبقاً.")
        return email

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("password1"), data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "كلمتا المرور غير متطابقتين.")
        if p1:
            try:
                password_validation.validate_password(p1, User(email=data.get("email"), full_name=data.get("full_name", "")))
            except forms.ValidationError as e:
                self.add_error("password1", e)
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if self.cleaned_data.get("wants_to_volunteer"):
            user.role = User.Role.VOLUNTEER
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["full_name", "phone_number", "city", "district", "profile_image"]
