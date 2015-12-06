from django import forms

from .models import Tweet, TweetStore
        
class TweetForm(forms.ModelForm):
    tweeet_store_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Tweet
        fields = ('author','content','tweeet_store_id')
        widgets = {
          'content': forms.Textarea(attrs={'rows':3, 'cols':15}),
        }

class TweetStoreForm(forms.ModelForm):
    class Meta:
        model = TweetStore
        fields = ('content','used')
        widgets = {
          'content': forms.Textarea(attrs={'rows':3, 'cols':15}),
        }
