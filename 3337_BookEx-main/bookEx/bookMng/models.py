from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
import json


class MainMenu(models.Model):
    item = models.CharField(max_length=200, unique=True)
    link = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.item


class Book(models.Model):
    name = models.CharField(max_length=200)
    web = models.URLField(max_length=200)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    publishdate = models.DateField(auto_now=True)
    picture = models.FileField(upload_to='bookEx/static/uploads')
    pic_path = models.CharField(max_length=300, editable=False, blank=True)
    username = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    favoritedby = models.TextField(default="[]", blank=True)

    # Rating fields
    number_of_ratings = models.PositiveIntegerField(default=0)
    avg_rating = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.id)

    # Rating update method
    def update_avg_rating(self):
        ratings = self.bookrating_set.all()
        total_ratings = ratings.count()
        average_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0.0

        if self.number_of_ratings != total_ratings or self.avg_rating != average_rating:
            self.number_of_ratings = total_ratings
            self.avg_rating = average_rating
            self.save(update_fields=['avg_rating', 'number_of_ratings'])

    # Method to get a specific user's rating for this book
    def get_user_rating(self, user):
        if not user.is_authenticated:
            return None
        book_rating = self.bookrating_set.filter(user=user).first()
        return book_rating.rating if book_rating else None


class Comment(models.Model):
    book = models.ForeignKey(Book, related_name='comments', on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.book.name}'


class BookRating(models.Model):
    rating = models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"Rating {self.rating} for {self.book.name} by {self.user.username}"

    def save(self, *args, **kwargs):
        # Prevent infinite recursion
        is_new = self.pk is None  # Check if this is a new instance
        super().save(*args, **kwargs)  # Save the current BookRating instance

        # Only update book stats if it's a new rating or the rating value changed
        if is_new or self.rating != self.book.avg_rating:
            self.book.update_avg_rating()
