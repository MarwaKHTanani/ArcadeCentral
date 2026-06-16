from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class GameManager(models.Manager):
    def validator(self, postData):
        errors = {}

        title = postData.get("title", "").strip()
        description = postData.get("description", "").strip()
        genre = postData.get("genre", "")
        platform = postData.get("platform", "")
        image_url = postData.get("image_url", "").strip()

        if len(title) < 2:
            errors["title"] = "Title must be at least 2 characters"

        if len(description) < 10:
            errors["description"] = "Description must be at least 10 characters"

        if genre == "":
            errors["genre"] = "Genre is required"

        if platform == "":
            errors["platform"] = "Platform is required"

        if image_url == "":
            errors["image_url"] = "Image URL is required"

        return errors


class Game(models.Model):

    GENRE_CHOICES = [
        ("ACTION", "Action"),
        ("RPG", "RPG"),
        ("HORROR", "Horror"),
        ("SPORTS", "Sports"),
    ]

    PLATFORM_CHOICES = [
        ("PC", "PC"),
        ("PS5", "PlayStation 5"),
        ("XBOX", "Xbox"),
        ("MOBILE", "Mobile"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    image_url = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    objects = GameManager()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class FavoriteGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
