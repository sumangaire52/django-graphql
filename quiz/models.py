from django.db import models
from django.contrib.auth import get_user_model


class Category(models.Model):
    title = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title


class Blog(models.Model):
    title = models.CharField(max_length=250)
    category = models.ManyToManyField(Category, related_name="blogs")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="blogs")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
