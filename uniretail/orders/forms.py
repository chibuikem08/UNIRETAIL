from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model  = Order
        fields = ['note']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['note'].widget = forms.Textarea(attrs={
            'class':       'form-control',
            'rows':        3,
            'placeholder': 'Any special instructions? e.g. "No onions", "Extra spicy"…'
        })
        self.fields['note'].required = False
        self.fields['note'].label    = 'Special Instructions (optional)'
