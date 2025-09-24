from django.db import models

# Create your models here.
class Category(models.Model):
    nom = models.CharField(max_length=100)
    description = models.CharField(max_length=300, default="")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom