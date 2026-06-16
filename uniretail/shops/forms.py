from django import forms
from .models import Shop, Product


class ShopForm(forms.ModelForm):
    class Meta:
        model  = Shop
        fields = ['name', 'category', 'description', 'logo', 'is_open']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'is_open':
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'rows': 3})


class ProductForm(forms.ModelForm):
    class Meta:
        model  = Product
        fields = ['name', 'category', 'description', 'price', 'image', 'stock', 'is_available']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'is_available':
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'rows': 3})
        self.fields['price'].widget.attrs.update({'placeholder': '0.00'})
