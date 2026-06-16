from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    """Registration form — buyers choose STUDENT or STAFF; vendors choose VENDOR."""

    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=False)

    ALLOWED_ROLES = [
        (CustomUser.Role.STUDENT, 'Student'),
        (CustomUser.Role.STAFF,   'University Staff'),
        (CustomUser.Role.VENDOR,  'Vendor (Shop Owner)'),
    ]

    role = forms.ChoiceField(choices=ALLOWED_ROLES)

    class Meta:
        model  = CustomUser
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'phone_number', 'role',
            'password1', 'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role  = self.cleaned_data['role']
        # Vendors start unapproved until admin reviews them
        if user.role == CustomUser.Role.VENDOR:
            user.is_approved_vendor = False
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
