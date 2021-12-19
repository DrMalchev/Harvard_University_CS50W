from django import forms
from django.contrib.auth.models import User
from django.db.models.enums import Choices
from django.db.models.fields import URLField


breadType = (
        ('White Bread', 'White Bread'),
        ('Country Bread', 'Country Bread'),
        ('Oat Porridge Bread', 'Oat Porridge Bread'),
        ('Semolina Bread', 'Semolina Bread'),
        ('100% Rye Bread', '100% Rye Bread'),
        ('Seeded', 'Seeded'),
        ('Baguette', 'Baguette'),
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
    comment = forms.CharField(label='Comment', max_length=256, required=False)
    #price = forms.FloatField(required=True, widget=forms.TextInput(attrs={'placeholder': '$3.5', 'size': 3, 'readonly': True}))
    price = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': '$3.5', 'size': 3, 'readonly': True}))
    
    
class EditForm(forms.Form):
    breadType = forms.ChoiceField(choices=breadType, required=True)
    quantity = forms.IntegerField(min_value=1, max_value=5, required=True)
    price = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 3, 'readonly': True}))

####
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = '__all__'

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class FileForm(forms.Form):
    file = forms.FileField()
    isTitleImage = forms.BooleanField(label="Use this photo as title image?", required=False)
    

