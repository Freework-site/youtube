from django import forms

class YouTubeForm(forms.Form):
    url = forms.URLField(label='YouTube URL', max_length=200)
