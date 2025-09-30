from django.db import models
  from django.contrib.auth.models import AbstractUser
  from django.core.validators import MinLengthValidator, MaxLengthValidator

  # Create your models here.

  class User(AbstractUser):
      avatar = models.ImageField(upload_to="avatars/")
      bio = models.TextField(max_length=500)


  class Category(models.Model):
      nom = models.CharField(max_length=100)
      description = models.CharField(max_length=300, default="")

      class Meta:
          verbose_name = "Catégorie"
          verbose_name_plural = "Catégories"

      def __str__(self):
          return self.nom

