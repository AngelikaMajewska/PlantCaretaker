from datetime import datetime

import pytest
from django.contrib.auth.models import User, Permission

from plants.models import Plant, OwnedPlants, Watering, SoilType, SoilIngredient, Event

# model_bakery !!!!!!!!!!!

@pytest.fixture
def plant():
    soil = SoilType.objects.create(name="Test Soil", description="Good for tests")
    return Plant.objects.create(
        name='Test Plant',
        description='Test description',
        soil=soil,
        light=1,
        watering_frequency=4
    )

@pytest.fixture
def three_plants():
    ing1 = SoilIngredient.objects.create(name="Compost", description="Nutrient-rich")
    ing2 = SoilIngredient.objects.create(name="Sand", description="Drains well")
    ing3 = SoilIngredient.objects.create(name="Peat", description="Retains moisture")

    soil1 = SoilType.objects.create(name="Soil A", description="Type A")
    soil1.ingredients.set([ing1])

    soil2 = SoilType.objects.create(name="Soil B", description="Type B")
    soil2.ingredients.set([ing2])

    soil3 = SoilType.objects.create(name="Soil C", description="Type C")
    soil3.ingredients.set([ing3])

    one = Plant.objects.create(
        name='Test Plant 1',
        description='Test description 1',
        soil=soil1,
        light=1,
        watering_frequency=4
    )
    two = Plant.objects.create(
        name='Test Plant 2',
        description='Test description 2',
        soil=soil2,
        light=2,
        watering_frequency=5
    )
    three = Plant.objects.create(
        name='Test Plant 3',
        description='Test description 3',
        soil=soil3,
        light=3,
        watering_frequency=6
    )
    return [one, two, three]

from django.test import Client
@pytest.fixture
def client():
    client = Client()
    return client

@pytest.fixture
def user_with_permission(db):
    user = User.objects.create_user(username='testuser', password='testpass')
    permission = Permission.objects.get(codename='add_plant')
    user.user_permissions.add(permission)
    user.save()
    return user

@pytest.fixture
def user_can_diagnose(db):
    user = User.objects.create_user(username='testuser', password='testpass')
    permission = Permission.objects.get(codename='can_diagnose')
    user.user_permissions.add(permission)
    user.save()
    return user

@pytest.fixture
def user_logged(db):
    user = User.objects.create_user(username='testuser', password='testpass')
    permission = Permission.objects.get(codename='add_plant')
    user.user_permissions.remove(permission)
    user.save()
    return user

@pytest.fixture
def event(user_logged):
    ing = SoilIngredient.objects.create(name="Peat", description="Retains moisture")
    soil = SoilType.objects.create(name="Soil C", description="Type C")
    soil.ingredients.set([ing])
    plant = Plant.objects.create(
        name='Test Plant 3',
        description='Test description 3',
        soil=soil,
        light=3,
        watering_frequency=6
    )
    event = Event.objects.create(name='Test Event', description='Test description',plant=plant,user=user_logged,date=datetime.now().today())
    return event
