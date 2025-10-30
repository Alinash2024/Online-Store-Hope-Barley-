"""Forms for the reviews app."""

from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Form for creating and updating reviews."""

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[
                    (i, f"{i} звезда{'ы' if i != 1 else ''}")
                    for i in range(1, 6)
                ],
                attrs={'class': 'Input'}
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'Textarea',
                    'placeholder': 'Поделитесь своим мнением о продукте',
                    'rows': 4
                }
            ),
        }
