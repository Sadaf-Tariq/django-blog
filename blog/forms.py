from .models import Comment, Rating
from django import forms


class CommentForm(forms.ModelForm):
    comment_hidden_field = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta:
        model = Comment
        fields = ('body',)


class RatingForm(forms.ModelForm):
    rating_hidden_field = forms.BooleanField(widget=forms.HiddenInput, initial=True)

    class Meta: 
        model = Rating
        fields = ('rating',)
        CHOICE = (
            ('0',0),
            ('1', 1),
            ('2', 2),
            ('3', 3),
            ('4', 4),
            ('5', 5),
            )
        widgets = {
            'rating': forms.Select(choices=CHOICE)
        }