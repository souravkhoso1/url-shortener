from django import forms

class URLForm(forms.Form):
    url = forms.URLField(
        label='Enter URL to shorten',
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com/very-long-url',
            'required': True
        })
    )