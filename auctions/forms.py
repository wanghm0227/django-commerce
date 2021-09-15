from django import forms
from .models import Lot
from django import forms
from djmoney.forms.widgets import MoneyWidget


class LotForm(forms.ModelForm):

    class Meta():
        auto_id = False

        model = Lot
        exclude = ['seller']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'bid': MoneyWidget(attrs={'class': 'form-control', 'placeholder': 'USD'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

        labels = {
            'bid': 'Starting bid',
        }

        help_texts = {
            'image': '<em>Choose a image as cover.</em>'
        }
