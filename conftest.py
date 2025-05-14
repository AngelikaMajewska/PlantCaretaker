import datetime

import pytest
from django.contrib.auth.models import User, Permission

from plants.models import Plant, OwnedPlants, Watering, SoilType, SoilIngredient, Event, WishList, OwnedPlantsManager, \
    UserLocation


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
    user = User.objects.create_user(username='testuser1', password='testpass')
    permission = Permission.objects.get(codename='add_plant')
    user.user_permissions.add(permission)
    user.save()
    return user

@pytest.fixture
def user_can_diagnose(db):
    user = User.objects.create_user(username='testuser2', password='testpass')
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
    UserLocation.objects.create(user=user, city='Warsaw',country='Poland')
    return user

# @pytest.fixture
# def event(user_logged):
#     ing = SoilIngredient.objects.create(name="Peat", description="Retains moisture")
#     soil = SoilType.objects.create(name="Soil C", description="Type C")
#     soil.ingredients.set([ing])
#     plant = Plant.objects.create(
#         name='Test Plant 3',
#         description='Test description 3',
#         soil=soil,
#         light=3,
#         watering_frequency=6
#     )
#
#     event = Event.objects.create(name='Test Event', description='Test description',plant=plant,user=user_logged,date=datetime.now().today())
#     return event

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

    event_date = datetime.date.today()
    event = Event.objects.create(
        name='Test Event',
        description='Test description',
        plant=plant,
        user=user_logged,
        date=event_date
    )
    return event

@pytest.fixture
def wishlist(user_logged):
    ing = SoilIngredient.objects.create(name="Peat", description="Retains moisture")
    soil = SoilType.objects.create(name="Soil C", description="Type C")
    soil.ingredients.set([ing])
    plant = Plant.objects.create(
        name='Test Plant',
        description='Test description',
        soil=soil,
        light=3,
        watering_frequency=6
    )
    wishlist = WishList.objects.create(owner=user_logged,plant=plant)
    return wishlist
@pytest.fixture
def multiple_wishlist(user_logged):
    ing = SoilIngredient.objects.create(name="Peat", description="Retains moisture")
    soil = SoilType.objects.create(name="Soil C", description="Type C")
    soil.ingredients.set([ing])

    # Tworzymy kilka roślin
    plant1 = Plant.objects.create(
        name='Test Plant 1',
        description='Test description 1',
        soil=soil,
        light=3,
        watering_frequency=6
    )
    plant2 = Plant.objects.create(
        name='Test Plant 2',
        description='Test description 2',
        soil=soil,
        light=2,
        watering_frequency=4
    )
    plant3 = Plant.objects.create(
        name='Test Plant 3',
        description='Test description 3',
        soil=soil,
        light=1,
        watering_frequency=5
    )

    # Tworzymy odpowiednie wpisy w wishlist
    wishlist = [
        WishList.objects.create(owner=user_logged, plant=plant1),
        WishList.objects.create(owner=user_logged, plant=plant2),
        WishList.objects.create(owner=user_logged, plant=plant3),
    ]
    return wishlist

@pytest.fixture
def owned_plants(user_logged):
    ing1 = SoilIngredient.objects.create(name="Compost", description="Nutrient-rich")
    soil = SoilType.objects.create(name="Soil A", description="Type A")
    soil.ingredients.set([ing1])

    plant_one = Plant.objects.create(
        name='Test Plant 1',
        description='Test description 1',
        soil=soil,
        light=1,
        watering_frequency=4
    )
    plant_two = Plant.objects.create(
        name='Test Plant 2',
        description='Test description 2',
        soil=soil,
        light=2,
        watering_frequency=5
    )
    plant_three = Plant.objects.create(
        name='Test Plant 3',
        description='Test description 3',
        soil=soil,
        light=3,
        watering_frequency=6
    )
    plant_list = [plant_one, plant_two, plant_three]
    owned =[]
    for plant in plant_list:
        owned_plant = OwnedPlants.objects.create_owned_plant_with_watering(owner=user_logged,plant=plant,owner_watering_frequency=1)
        owned.append(owned_plant)
    return owned

@pytest.fixture
def owned_plants_user_can_diagnose(user_can_diagnose):
    ing1 = SoilIngredient.objects.create(name="Compost", description="Nutrient-rich")
    soil = SoilType.objects.create(name="Soil A", description="Type A")
    soil.ingredients.set([ing1])

    plant_one = Plant.objects.create(
        name='Test Plant 1',
        description='Test description 1',
        soil=soil,
        light=1,
        watering_frequency=4
    )
    plant_two = Plant.objects.create(
        name='Test Plant 2',
        description='Test description 2',
        soil=soil,
        light=2,
        watering_frequency=5
    )
    plant_three = Plant.objects.create(
        name='Test Plant 3',
        description='Test description 3',
        soil=soil,
        light=3,
        watering_frequency=6
    )
    plant_list = [plant_one, plant_two, plant_three]
    owned =[]
    for plant in plant_list:
        owned_plant = OwnedPlants.objects.create_owned_plant_with_watering(owner=user_can_diagnose,plant=plant,owner_watering_frequency=1)
        owned.append(owned_plant)
    return owned