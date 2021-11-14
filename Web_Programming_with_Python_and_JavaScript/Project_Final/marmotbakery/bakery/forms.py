from django import forms
from django.db.models.enums import Choices
from django.db.models.fields import URLField

breadType = (
        ('White Bread', 'White Bread'),
        ('Country Bread', 'Country Bread'),
        ('Oat Porridge Bread', 'Oat Porridge Bread'),
        ('Semolina Bread', 'Semolina Bread'),
        ('100% Rye Bread', '100% Rye Bread'),
        ('Focaccia', 'Focaccia'),
        ('Toast Bread', 'Toast Bread'),
        ('Sweet Brioche', 'Sweet Brioche')
    )


class PlaceOrderForm(forms.Form):
    breadType = forms.ChoiceField(choices=breadType, required=True)
    quantity = forms.IntegerField(min_value=1, max_value=5, required=True)
    firstName = forms.CharField(label='First Name', max_length=64, required=True)
    lastName = forms.CharField(label='First Name', max_length=64, required=True)
    city = forms.CharField(label='city', max_length=64, required=True)
    postCode = forms.IntegerField(label='Postal Code', required=True)
    addressL1 = forms.CharField(label='Address Line 1', max_length=64, required=True)
    addressL2 = forms.CharField(label='Address Line 2', max_length=64, required=False)
    tel = forms.IntegerField(label='Telephone Number', max_value=9999999999, required=True)
    comment = forms.CharField(label='Comment', max_length=256, required=False, widget=forms.Textarea(attrs={'cols': 50, 'rows': 2}))
    #price = forms.FloatField(required=True, widget=forms.TextInput(attrs={'placeholder': '$3.5', 'size': 3, 'readonly': True}))
    price = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': '$3.5', 'size': 3, 'readonly': True}))
    
    
