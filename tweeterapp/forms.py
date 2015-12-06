from django import forms

from .models import Tweet
        
class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ('author','content')
        widgets = {
          'content': forms.Textarea(attrs={'rows':3, 'cols':15}),
        }
        