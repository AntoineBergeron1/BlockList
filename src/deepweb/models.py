from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MaxLengthValidator

# Create your models here.


class User(AbstractUser):
    avatar = models.ImageField(upload_to="avatars/")
    bio = models.TextField(max_length=500)
