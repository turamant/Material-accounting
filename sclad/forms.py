from django import forms
from .models import (Product, Arrival, ArrivalComposition, Supplier, Expense,
                     Customer, ExpenseComposition)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['article_number', 'name', 'description', 'purchase_price', 'sell_price',
                  'quantity']


class ArrivalForm(forms.ModelForm):
    class Meta:
        model = Arrival
        fields = ['date', 'supplier', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'customer', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
        }


class ExpenseCompositionForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label='Продукт', required=True)
    quantity = forms.IntegerField(min_value=0, initial=0, label='Количество')

    class Meta:
        model = ExpenseComposition
        fields = ['product', 'quantity']


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'

