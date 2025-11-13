from django import forms
from .models import ProductType, MaterialType


class MaterialCalculationForm(forms.Form):
    product_type = forms.ModelChoiceField(
        queryset=ProductType.objects.all(),
        label="Тип продукции",
        widget=forms.Select(attrs={
            'class': 'uk-select',
            'style': 'border-radius: 10px;'
        })
    )

    material_type = forms.ModelChoiceField(
        queryset=MaterialType.objects.all(),
        label="Тип материала",
        widget=forms.Select(attrs={
            'class': 'uk-select',
            'style': 'border-radius: 10px;'
        })
    )

    product_quantity = forms.IntegerField(
        min_value=1,
        label="Количество продукции",
        widget=forms.NumberInput(attrs={
            'class': 'uk-input',
            'style': 'border-radius: 10px;',
            'placeholder': 'Введите количество'
        })
    )

    param1 = forms.FloatField(
        min_value=0.01,
        label="Параметр продукции 1",
        widget=forms.NumberInput(attrs={
            'class': 'uk-input',
            'style': 'border-radius: 10px;',
            'placeholder': 'Введите первый параметр',
            'step': '0.01'
        })
    )

    param2 = forms.FloatField(
        min_value=0.01,
        label="Параметр продукции 2",
        widget=forms.NumberInput(attrs={
            'class': 'uk-input',
            'style': 'border-radius: 10px;',
            'placeholder': 'Введите второй параметр',
            'step': '0.01'
        })
    )