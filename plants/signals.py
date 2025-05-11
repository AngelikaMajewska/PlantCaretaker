# myapp/signals.py
from datetime import datetime, timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OwnedPlants, Watering  # przykładowy model


