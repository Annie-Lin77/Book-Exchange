from django import forms
from django.forms import ModelForm
from .models import Book, BookRating


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = [
            'name',
            'web',
            'price',
            'picture',

        ]

#Form for book rating
class RatingForm(forms.ModelForm):
    RATING_CHOICES = [(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]
    #Rating field, using a choice field to display a dropdown
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.RadioSelect)
    class Meta:
        model = BookRating
        fields = ['rating']
