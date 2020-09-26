from django.db import models
from django.contrib.auth.models import User

# Register your models here.

# class Wishlist(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     book_id = models.IntegerField()
#     title = models.CharField(max_length=100)
#     def __str__(self):
#         return self.name

# class Comment(models.Model):
#     content = models.CharField(max_length=250)
#     book_id = models.IntegerField()
#     user = models.ForeignKey(User, on_delete=models.CASCADE)

#     def str(self):
#         return self.itemName
