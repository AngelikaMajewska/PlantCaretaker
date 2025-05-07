# myapp/signals.py
from datetime import datetime, timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OwnedPlants, Watering  # przykładowy model

@receiver(post_save, sender=OwnedPlants)
def create_watering(sender, instance, created, **kwargs):
    if created:
        # existing = Watering.objects.filter(user_id = instance.owner.id, plant_id = instance.plant.id).exists()
        # if not existing:
        watering = Watering.objects.create(
            user_id=instance.owner.id,
            plant_id=instance.plant.id,
            date = (datetime.now() - timedelta(days=3)).date(),
            next_watering=datetime.now().date() + timedelta(days=3)
        )
        watering.save()



@receiver(post_save, sender=OwnedPlants)
def watering_frequency_change(sender, instance, created, **kwargs):
    if not created:
        # Możesz dodać logikę sprawdzającą, czy to owner_watering_frequency się zmieniło
        owner_id = instance.owner.id
        plant_id = instance.plant.id
        frequency = int(instance.owner_watering_frequency)
        waterings= Watering.objects.filter(user_id=owner_id, plant_id=plant_id).order_by('-date')
        watering = waterings[0]
        watering.next_watering = datetime.now()+timedelta(days=frequency)
        watering.save()
