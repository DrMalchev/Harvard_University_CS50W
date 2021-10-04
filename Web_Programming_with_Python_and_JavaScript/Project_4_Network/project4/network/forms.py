from django import forms
from django.db.models.fields import URLField



class AddPostForm(forms.Form):
    
    body = forms.CharField(label='New Post', max_length=256, required=True, widget=forms.Textarea(attrs={'cols': 50, 'rows': 2}))


