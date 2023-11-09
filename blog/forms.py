from .models import Comment, Rating
from django import forms


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)


class RatingForm(forms.ModelForm):
    class Meta: 
        model = Rating
        fields = ('rating',)
        CHOICE = (
            ('1', 1),
            ('2', 2),
            ('3', 3),
            ('4', 4),
            ('5', 5),
            )
        widgets = {
            'rating': forms.Select(choices=CHOICE)
        }