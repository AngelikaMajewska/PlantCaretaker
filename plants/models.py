from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from datetime import date, timedelta, timezone, datetime
import re

LIGHT_TYPES = (
    (0,'Unknown'),
    (1,'Direct sunlight'),
    (2,'Bright indirect sunlight'),
    (3,'Indirect sunlight'),
    (4,'Half-shadow'),
    (5,'Shadow'),
)

class Plant(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    soil = models.ForeignKey('SoilType', on_delete=models.SET_NULL, null=True, blank=True)
    light = models.IntegerField(choices=LIGHT_TYPES)
    image = models.ImageField(upload_to='plant_images/', null=True, blank=True)
    watering_frequency = models.IntegerField(validators=[MinValueValidator(1)], default=3)

    def __str__(self):
        return self.name

class Event(models.Model):
    plant=models.ForeignKey(Plant, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class PlantDetailComments(models.Model):
    plant=models.ForeignKey(Plant, on_delete=models.CASCADE)
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plant} {self.date} {self.user}"

class UserNotes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    date = models.DateField(auto_now_add=True)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user} {str(self.date)} {self.plant}"

class AIRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    note = models.TextField(default='')
    date = models.DateField(auto_now_add=True)


class Watering(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plant = models.ForeignKey('Plant', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    fertiliser = models.BooleanField(default=False)
    next_watering = models.DateField(blank=True, null=True, default=None)

    def clean(self):
        super().clean()
        if self.next_watering and self.next_watering < self.date:
            raise ValidationError("Next watering date cannot be earlier than the watering date.")

    def save(self, *args, **kwargs):
        if not self.next_watering:
            today = datetime.now().date()
            self.next_watering = today + timedelta(days=self.plant.watering_frequency)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plant.name}, {self.date}, {self.user}"

class SoilIngredient(models.Model):
    name=models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class SoilType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    ingredients = models.ManyToManyField(SoilIngredient)

    def __str__(self):
        return self.name

class OwnedPlants(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    plant=models.ForeignKey(Plant, on_delete=models.CASCADE)
    owner_watering_frequency = models.IntegerField(null=True,blank=True,validators=[MinValueValidator(1)])

    class Meta:
        unique_together = (('owner', 'plant'),)
        permissions = [
            ("can_diagnose", "Can diagnose plants"),
        ]

    def __str__(self):
        return f"{self.owner}, {self.plant}"

class WishList(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    plant=models.ForeignKey(Plant, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('owner', 'plant'),)

    def __str__(self):
        return f"{self.owner}, {self.plant}"

class PlantUserPhotos(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='plant_user_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.owner}, {self.plant}"

class PlantTips(models.Model):
    tip=models.TextField()

    def __str__(self):
        return self.tip

class UserLocation(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    city=models.CharField(max_length=100)
    country=models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return f"{self.user}, {self.city}, {self.country}"
