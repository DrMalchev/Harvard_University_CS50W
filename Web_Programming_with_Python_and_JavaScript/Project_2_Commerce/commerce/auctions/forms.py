
from django import forms
from django.db.models.fields import URLField

categories = (
        ('Fashion', 'Fashion'),
        ('Toys', 'Toys'),
        ('Electronics', 'Electronics'),
        ('Home', 'Home'),
        ('Other', 'Other')
    )

class AddListingForm(forms.Form):
    title = forms.CharField(label='Title', max_length=64, required=True)
    description = forms.CharField(label='Description', max_length=256, required=True, widget=forms.Textarea(attrs={'cols': 50, 'rows': 2}))
    category = forms.ChoiceField(choices=categories, required=False)
    image_url = forms.URLField(required=False)
    starting_bid = forms.FloatField(min_value=0.01, required=True)

class AddCommentForm(forms.Form):
    comment = forms.CharField(label='Write Your comment here...', max_length=256, required=True, widget=forms.Textarea(attrs={'cols': 50, 'rows': 2}))