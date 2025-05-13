# import pytest
#
# from exercises_app.views import ProductView
#
# @pytest.mark.django_db
# def test_product_detail(product, client):
#     response = client.get(f'/product/{product.pk}/')
#     assert response.status_code == 200
#     name = response.context['name']
#     description = response.context['description']
#     price = response.context['price']
#     assert name == product.name
#     assert description == product.description
#     assert price == product.price


import pytest
from django.urls import reverse

from plants.models import Plant, SoilType
# from functions import ...

# PlantDetailView
@pytest.mark.django_db
def test_plant_detail(plant, client,user_with_permission):
    client.login(username='testuser', password='testpass')
    response = client.get(f'/plants/{plant.pk}/')
    assert response.status_code == 200
    name = response.context['plant'].name
    description = response.context['plant'].description
    assert plant.name == name
    assert plant.description == description

# PlantDetailView
@pytest.mark.django_db
def test_plant_detail_does_not_exist(client):
    response = client.get(f'/plants/12222/')
    assert response.status_code == 404

# AddPlantView
@pytest.mark.django_db
def test_add_plant(client,user_with_permission):
    client.force_login(user_with_permission)
    soil = SoilType.objects.create(
        name="Test Soil",
        description="Test soil for banana plant"
    )

    data = {
        'name': 'Banana',
        'description': 'Banana description',
        'light': 1,
        'soil': soil.pk , # ← używamy istniejącego ID
        'watering_frequency':5
    }
    response = client.post('/addplant/', data)
    assert response.status_code == 302
    plant = Plant.objects.get(name=data['name'])
    assert plant.description == data['description']
    assert plant.light == data['light']
    assert plant.soil == soil

# AddPlantView
@pytest.mark.django_db
def test_add_plant_fail(client,user_with_permission):
    client.force_login(user_with_permission)
    data = {
        'name': 'Banana',
        'description': 'Banana description',
    }
    response = client.post('/addplant/', data)
    assert response.status_code == 200
    assert response.context['form'].errors

# AddPlantView
def test_add_plant_form_display(client,user_with_permission):
    client.force_login(user_with_permission)
    response = client.get('/addplant/')
    assert response.status_code == 200
    assert response.context['form']

# AddPlantView
def test_add_plant_form_display_fail(client):
    response = client.get('/addplant/')
    assert response.status_code == 302

# AddPlantView
def test_add_plant_form_display_nologin_fail(client, user_logged):
    client.force_login(user_logged)
    response = client.get('/addplant/')
    assert response.status_code == 403

#CatalogView
@pytest.mark.django_db
def test_list_plants(three_plants,client):
    response = client.get(f'/catalog/')
    assert response.status_code == 200
    assert len(response.context['plants']) == len(three_plants)
    view_plants = [plant.name for plant in response.context['plants']]
    result_list = ['Test Plant 1','Test Plant 2','Test Plant 3']
    assert view_plants == result_list

#CatalogView
@pytest.mark.django_db
def test_ai_logged(client, user_logged):
    client.force_login(user_logged)
    response = client.get('/catalog/')
    assert response.status_code == 200
    html = response.content.decode()
    assert 'diagnosis-box' not in html

#CatalogView
@pytest.mark.django_db
def test_ai_not_logged(client, user_can_diagnose):
    client.force_login(user_can_diagnose)
    response = client.get('/catalog/')
    assert response.status_code == 200
    html = response.content.decode()
    assert 'diagnosis-box' in html

#Calendar
@pytest.mark.django_db
def test_calendar_fail(client):
    response = client.get('/calendar/')
    assert response.status_code == 302

#Calendar
@pytest.mark.django_db
def test_calendar_logged(client,user_logged):
    client.force_login(user_logged)
    response = client.get('/calendar/')
    assert response.status_code == 200

#AddEventView
@pytest.mark.django_db
def test_add_event(client,user_logged,event):
    client.force_login(user_logged)
    event = {
        'name': event.name,
        'description': event.description,
        'date': event.date.strftime('%Y-%m-%d'),
        'plant': event.plant.pk,
    }
    response = client.post('/add-event/', event)
    assert response.status_code == 200
    assert response.json()['success'] is True

#AddEventView
@pytest.mark.django_db
def test_add_event_missing_data_fail(client,user_logged,event):
    client.force_login(user_logged)
    event = {
        'description': event.description,
        'date': event.date.strftime('%Y-%m-%d'),
        'plant': event.plant.pk,
    }
    response = client.post('/add-event/', event)
    assert response.status_code == 200
    assert response.json()['success'] is False

#AddEventView
@pytest.mark.django_db
def test_add_event_fail(client,event):
    event = {
        'name': event.name,
        'description': event.description,
        'date': event.date.strftime('%Y-%m-%d'),
        'plant': event.plant.pk,
    }
    response = client.post('/add-event/', event)
    assert response.status_code == 302
    assert '/login' in response.url or '/accounts/login' in response.url

#PlantDetailView
@pytest.mark.django_db
def test_pdf_generate(client, plant):
    response = client.get(f'/plants/{plant.pk}/')
    assert response.status_code == 200
    html = response.content.decode()
    assert 'generate-plant-pdf' in html

@pytest.mark.django_db
def test_generate_plant_pdf(client,plant):
    url = reverse('generate-plant-pdf', args=[plant.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert 'Content-Disposition' in response
    assert f'{plant.name}_detail.pdf' in response['Content-Disposition']
    assert len(response.content) > 100

@pytest.mark.django_db
def test_add_comment_logged(client, plant,user_logged):
    client.force_login(user_logged)
    response = client.get(f'/plants/{plant.pk}/')
    assert response.status_code == 200
    html = response.content.decode()
    assert 'add-comment-form' in html

@pytest.mark.django_db
def test_add_comment_not_logged(client, plant):
    response = client.get(f'/plants/{plant.pk}/')
    assert response.status_code == 200
    html = response.content.decode()
    assert 'add-comment-form' not in html

#AllEventsView