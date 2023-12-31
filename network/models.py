from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    followed_by = models.ManyToManyField(User, blank=True, related_name="following")
    
    def __str__(self):
        return f"{self.user} is followed by: {self.followed_by}"

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    postText = models.CharField(max_length=255)
    posted = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(User, blank=True, related_name="likes")

    def __str__(self):
        return f"{self.author} tweeted: {self.postText}"