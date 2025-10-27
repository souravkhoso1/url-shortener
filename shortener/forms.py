# shortener/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import ShortenedURL, UserProfile
import re


class URLForm(forms.Form):
    url = forms.URLField(
        label='Enter URL to shorten',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com/very-long-url',
            'required': True
        })
    )
    custom_code = forms.CharField(
        label='Custom short code (optional)',
        required=False,
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'my-custom-code (optional)',
        })
    )

    def clean_custom_code(self):
        custom_code = self.cleaned_data.get('custom_code')
        if custom_code:
            # Validate format: alphanumeric and hyphens only
            if not re.match(r'^[a-zA-Z0-9-]+$', custom_code):
                raise forms.ValidationError('Short code can only contain letters, numbers, and hyphens.')

            # Check minimum length
            if len(custom_code) < 3:
                raise forms.ValidationError('Short code must be at least 3 characters long.')

            # Check if already exists
            if ShortenedURL.objects.filter(short_code=custom_code).exists():
                raise forms.ValidationError('This short code is already taken. Please choose another.')

            # Reserved words
            reserved = ['admin', 'login', 'logout', 'register', 'my-urls', 'stats', 'api']
            if custom_code.lower() in reserved:
                raise forms.ValidationError('This short code is reserved. Please choose another.')

        return custom_code


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class PasswordResetRequestForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'required': True
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('No user found with this username.')
        return username


class PasswordResetConfirmForm(forms.Form):
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'required': True
        })
    )
    password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter new password',
            'required': True
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Passwords do not match.')
            if len(password1) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long.')

        return cleaned_data


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }


class ProfilePhotoUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['photo']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }