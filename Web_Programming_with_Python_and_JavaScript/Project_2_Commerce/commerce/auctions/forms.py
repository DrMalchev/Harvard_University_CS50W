from django import forms

categories = (
        (1, 'Fashion'),
        (2, 'Toys'),
        (3, 'Electronics'),
        (4, 'Home'),
        (5, 'Other')
    )

class AddListingForm(forms.Form):
    title = forms.CharField(label='Title', max_length=64, required=True)
    description = forms.CharField(label='Description', max_length=128, required=True)
    category = forms.ChoiceField(choices=categories)
    image_url = forms.URLField()
    starting_bid = forms.FloatField(min_value=0.01, required=True)
