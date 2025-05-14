import json
from datetime import date, timedelta
from django.contrib.auth.models import User
from io import BytesIO
from pypdf import PdfReader

import pytest
from django.urls import reverse

from plants.models import Plant, SoilType, WishList, Watering, OwnedPlants


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
def test_add_plant_with_permission(client,user_with_permission):
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
def test_add_plant_missing_data_fail(client,user_with_permission):
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
def test_add_plant_form_display_not_logged_fail(client):
    response = client.get('/addplant/')
    assert response.status_code == 302

# AddPlantView
def test_add_plant_form_display_no_permission_fail(client, user_logged):
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

#Icons of Wishlist for Catalog
@pytest.mark.django_db
def test_icons_visible_logged(client, user_logged, plant):
    client.force_login(user_logged)
    response = client.get('/catalog/')
    assert response.status_code == 200
    html = response.content.decode()
    assert 'to-wishlist' in html or 'wishlisted' in html or 'owned-catalog-icon' in html

#Icons of Wishlist for Catalog
@pytest.mark.django_db
def test_icons_visible_not_logged_fail(client, plant):
    response = client.get('/catalog/')
    assert response.status_code == 200
    html = response.content.decode()
    assert 'to-wishlist' not in html and 'wishlisted' not in html and 'owned-catalog-icon' not in html

#WhatPlantView for Catalog
@pytest.mark.django_db
def test_ai_form_logged(client, user_logged):
    client.force_login(user_logged)
    response = client.get('/catalog/')
    assert response.status_code == 200
    html = response.content.decode()
    assert 'diagnosis-box' not in html

#WhatPlantView for Catalog
@pytest.mark.django_db
def test_ai_form_not_logged(client):
    response = client.get('/catalog/')
    assert response.status_code == 200
    html = response.content.decode()
    assert 'diagnosis-box' not in html

#WhatPlantView for Catalog
@pytest.mark.django_db
def test_ai_form_permission(client, user_can_diagnose):
    client.force_login(user_can_diagnose)
    response = client.get('/catalog/')
    assert response.status_code == 200
    html = response.content.decode()
    assert 'diagnosis-box' in html

#AddToWishlistView for Catalog
@pytest.mark.django_db
def test_add_to_wishlist(client,plant,user_logged):
    client.force_login(user_logged)
    to_wishlist = {
        'plant_id': plant.pk,
        'owner_id': user_logged.pk,
    }
    response = client.post('/add-to-wishlist/', data=json.dumps(to_wishlist), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is True

#AddToWishlistView for Catalog
@pytest.mark.django_db
def test_add_to_wishlist_double_data_fail(client,plant,user_logged):
    client.force_login(user_logged)
    to_wishlist = {
        'plant_id': plant.pk,
        'owner_id': user_logged.pk,
    }
    first_response = client.post('/add-to-wishlist/', data=json.dumps(to_wishlist), content_type='application/json')
    second_response = client.post('/add-to-wishlist/', data=json.dumps(to_wishlist), content_type='application/json')
    assert second_response.status_code == 200
    assert second_response.json()['success'] is False
    assert second_response.json()['error'] == "Plant already in wishlist."

#AddToWishlistView for Catalog
@pytest.mark.django_db
def test_add_to_wishlist_not_logged_fail(client):
    response = client.get('/add-to-wishlist/')
    assert response.status_code == 302

#RemoveFromWishlistView for Catalog
@pytest.mark.django_db
def test_remove_from_wishlist(client,wishlist,user_logged):
    client.force_login(user_logged)
    plant = wishlist.plant_id
    owner = wishlist.owner_id
    from_wishlist = {
        'plant_id': plant,
        'owner_id': owner,
    }
    response = client.post('/remove-from-wishlist/', data=json.dumps(from_wishlist), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is True

#RemoveFromWishlistView for Catalog
@pytest.mark.django_db
def test_remove_from_wishlist_doesnt_exist_fail(client,wishlist,user_logged):
    client.force_login(user_logged)
    owner_id = wishlist.owner_id
    from_wishlist = {
        'plant_id': 125676,
        'owner_id': owner_id,
    }
    response = client.post('/remove-from-wishlist/', data=json.dumps(from_wishlist), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is False
    assert response.json()['error'] == "No WishList matches the given query."

#RemoveFromWishlistView for Catalog
@pytest.mark.django_db
def test_remove_from_wishlist_not_logged_fail(client):
    response = client.get('/remove-from-wishlist/')
    assert response.status_code == 302

#PlantDetailView
@pytest.mark.django_db
def test_pdf_generate_button_visible(client, plant):
    response = client.get(f'/plants/{plant.pk}/')
    assert response.status_code == 200
    html = response.content.decode()
    assert 'generate-plant-pdf' in html

#generate_plant_pdf for PlantDetailView
@pytest.mark.django_db
def test_generate_plant_pdf(client,plant):
    response = client.get(f'/generate-plant-pdf/{plant.pk}/')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    content = response.content
    assert len(content) > 100
    assert 'attachment' in response.get('Content-Disposition', '')
    pdf_reader = PdfReader(BytesIO(response.content))
    text = ''
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    assert f"{plant.name}" in text
    assert f"{plant.description}" in text

#AddCommentView for PlantDetailView
@pytest.mark.django_db
def test_add_comment_form_logged(client, plant,user_logged):
    client.force_login(user_logged)
    response = client.get(f'/plants/{plant.pk}/')
    assert response.status_code == 200
    html = response.content.decode()
    assert 'add-comment-form' in html

#AddCommentView for PlantDetailView
@pytest.mark.django_db
def test_add_comment_form_not_logged(client, plant):
    response = client.get(f'/plants/{plant.pk}/')
    assert response.status_code == 200
    html = response.content.decode()
    assert 'add-comment-form' not in html

#AddCommentView for PlantDetailView
@pytest.mark.django_db
def test_add_comment(client,plant,user_logged):
    client.force_login(user_logged)
    data={
        'plant_id': plant.pk,
        'comment': 'test comment',
    }
    response = client.post( '/add-comment/', data=json.dumps(data), content_type='application/json' )
    assert response.status_code == 200
    assert response.json()['success'] is True

#AddCommentView for PlantDetailView
@pytest.mark.django_db
def test_add_comment_empty_fail(client,plant,user_logged):
    client.force_login(user_logged)
    data = {
        'plant_id': plant.pk,
    }
    response = client.post('/add-comment/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is False
    assert response.json()['error'] == "Comment cannot be empty."

#AddCommentView for PlantDetailView
@pytest.mark.django_db
def test_add_comment_method_get_fail(client,plant,user_logged):
    client.force_login(user_logged)
    response = client.get('/add-comment/')
    assert response.status_code == 200
    assert response.json()['success'] is False
    assert response.json()['error'] == "Invalid request method."

#CalendarView
@pytest.mark.django_db
def test_calendar_not_logged_fail(client):
    response = client.get('/calendar/')
    assert response.status_code == 302

#CalendarView
@pytest.mark.django_db
def test_calendar_logged(client,user_logged):
    client.force_login(user_logged)
    response = client.get('/calendar/')
    assert response.status_code == 200

#AddEventView for CalendarView
@pytest.mark.django_db
def test_add_event(client,user_logged,event):
    client.force_login(user_logged)
    event = {
        'name': event.name,
        'description': event.description,
        'date': event.date,
        'plant': event.plant.pk,
    }
    response = client.post('/add-event/', event)
    assert response.status_code == 200
    assert response.json()['success'] is True

#AddEventView for CalendarView
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

#AddEventView for CalendarView
@pytest.mark.django_db
def test_add_event_not_logged_fail(client,event):
    event = {
        'name': event.name,
        'description': event.description,
        'date': event.date.strftime('%Y-%m-%d'),
        'plant': event.plant.pk,
    }
    response = client.post('/add-event/', event)
    assert response.status_code == 302
    assert '/login' in response.url or '/accounts/login' in response.url

#FinishEventView for CalendarView
@pytest.mark.django_db
def test_finish_event_logged(client,user_logged,event):
    client.force_login(user_logged)
    event.user = user_logged
    data={
        'event_id': event.pk,
    }
    response = client.post('/finish-event/', data=json.dumps(data),content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is True

#FinishEventView for CalendarView
@pytest.mark.django_db
def test_finish_event_wrong_id_fail(client,user_logged,event):
    client.force_login(user_logged)
    event.user = user_logged
    data={
        'event_id': 14534,
    }
    response = client.post('/finish-event/', data=json.dumps(data),content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is False

#FinishEventView for CalendarView
@pytest.mark.django_db
def test_finish_event_not_logged(client,event):
    data={
        'event_id': event.pk,
    }
    response = client.post('/finish-event/', data=json.dumps(data),content_type='application/json')
    assert response.status_code == 302

#CancelEventView for CalendarView
@pytest.mark.django_db
def test_cancel_event_logged(client,user_logged,event):
    client.force_login(user_logged)
    event.user = user_logged
    data={
        'event_id': event.pk,
    }
    response = client.post('/cancel-event/', data=json.dumps(data),content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is True

#CancelEventView for CalendarView
@pytest.mark.django_db
def test_cancel_event_wrong_id_fail(client,user_logged,event):
    client.force_login(user_logged)
    event.user = user_logged
    data={
        'event_id': 14534,
    }
    response = client.post('/cancel-event/', data=json.dumps(data),content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is False

#CancelEventView for CalendarView
@pytest.mark.django_db
def test_cancel_event_not_logged(client,event):
    data={
        'event_id': event.pk,
    }
    response = client.post('/cancel-event/', data=json.dumps(data),content_type='application/json')
    assert response.status_code == 302

# DashboardView
@pytest.mark.django_db
def test_dashboard_not_logged_fail(client):
    response = client.get('/dashboard/')
    assert response.status_code == 302

#DashboardView
@pytest.mark.django_db
def test_dashboard_logged(client,user_logged,owned_plants,multiple_wishlist):
    client.force_login(user_logged)
    response = client.get('/dashboard/')
    assert response.status_code == 200
    html = response.content.decode()
    for current_plant in owned_plants:
        assert str(current_plant.plant.name) in html
        assert Watering.objects.filter(user=user_logged, plant=current_plant.plant).exists()
    for plant in multiple_wishlist:
        assert WishList.objects.filter(owner=user_logged, plant_id=plant.plant.pk).exists()

#MoveWateringView for DashboardView
@pytest.mark.django_db
def test_watering_logged(client,user_logged,owned_plants):
    client.force_login(user_logged)
    waterings = Watering.objects.filter(user=user_logged)
    data ={
        'watering_id': waterings[0].pk,
        'plant_id': waterings[0].plant.pk,
        'days': 1,
    }
    response = client.post('/move-watering/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is True

#MoveWateringView for DashboardView
@pytest.mark.django_db
def test_watering_not_logged(client,user_logged,owned_plants):
    waterings = Watering.objects.filter(user=user_logged)
    data ={
        'watering_id': waterings[0].pk,
        'plant_id': 12435,
        'days': 1,
    }
    response = client.post('/move-watering/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 302

#MoveWateringView for DashboardView
@pytest.mark.django_db
def test_watering_wrong_plant_fail(client,user_logged,owned_plants):
    client.force_login(user_logged)
    waterings = Watering.objects.filter(user=user_logged)
    data ={
        'watering_id': waterings[0].pk,
        'plant_id': 12435,
        'days': 1,
    }
    response = client.post('/move-watering/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is False
    assert response.json()['error'] == "Invalid data"

#MoveWateringView for DashboardView
@pytest.mark.django_db
def test_watering_wrong_id_fail(client,user_logged,owned_plants):
    client.force_login(user_logged)
    waterings = Watering.objects.filter(user=user_logged)
    data ={
        'watering_id': 1245,
        'plant_id': waterings[0].plant.pk,
        'days': 1,
    }
    response = client.post('/move-watering/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is False
    assert response.json()['error'] == "No Watering matches the given query."

#MoveWateringView for DashboardView
@pytest.mark.django_db
def test_watering_wrong_days_fail(client,user_logged,owned_plants):
    client.force_login(user_logged)
    waterings = Watering.objects.filter(user=user_logged)
    data ={
        'watering_id': waterings[0].pk,
        'plant_id': waterings[0].plant.pk,
        'days': 5,
    }
    response = client.post('/move-watering/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is False
    assert response.json()['error'] == "Invalid count of days."

#FinishWateringView for DashboardView
@pytest.mark.django_db
def test_finish_watering_logged(client,user_logged,owned_plants):
    client.force_login(user_logged)
    waterings = Watering.objects.filter(user=user_logged)
    data ={
        'watering_id': waterings[0].pk,
        'fertilizer': "True",
    }
    response = client.post('/finish-watering/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is True

#FinishWateringView for DashboardView
@pytest.mark.django_db
def test_finish_watering_not_logged_fail(client,user_logged,owned_plants):
    waterings = Watering.objects.filter(user=user_logged)
    data ={
        'watering_id': waterings[0].pk,
        'fertilizer': "True",
    }
    response = client.post('/finish-watering/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 302

#FinishWateringView for DashboardView
@pytest.mark.django_db
def test_finish_watering_wrong_id_fail(client,user_logged,owned_plants):
    client.force_login(user_logged)
    data ={
        'watering_id': 42335,
        'fertilizer': "True",
    }
    response = client.post('/finish-watering/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['error'] == "No Watering matches the given query."

#FinishWateringView for DashboardView
@pytest.mark.django_db
def test_finish_watering_user_not_owner_of_plant_fail(client, user_logged, three_plants):
    client.force_login(user_logged)
    other_user = User.objects.create_user(username="otheruser", password="otherpass")
    foreign_plant = three_plants[0]
    watering = Watering.objects.create(
        user=other_user,
        plant=foreign_plant,
        date=date.today(),
        fertiliser=False,
        next_watering=date.today() + timedelta(days=5)
    )
    data = {'watering_id': watering.pk, 'fertilizer': "True"}
    response = client.post('/finish-watering/', data=json.dumps(data), content_type='application/json')

    # Sprawdzamy odpowiedź
    assert response.status_code == 200
    assert response.json()['success'] is False
    assert response.json()['error'] == "No OwnedPlants matches the given query."

#GeneratePDFView for DashboardView
@pytest.mark.django_db
def test_dashboard_pdf_generate(client, user_logged,event,multiple_wishlist,owned_plants):
    client.force_login(user_logged)
    response = client.get(f'/generate-pdf/')
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    content = response.content
    assert len(content) > 100
    assert 'attachment' in response.get('Content-Disposition', '')
    pdf_reader = PdfReader(BytesIO(response.content))
    text = ''
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    assert "Events of the month" in text
    assert "Wishlist" in text
    assert "Planned waterings" in text
    assert "No events added." not in text
    assert "No plants added." not in text

#GeneratePDFView for DashboardView
@pytest.mark.django_db
def test_dashboard_pdf_generate_no_data_fail(client, user_logged):
    client.force_login(user_logged)
    response = client.get('/generate-pdf/')

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert 'attachment' in response.get('Content-Disposition', '')

    pdf_reader = PdfReader(BytesIO(response.content))
    text = ''
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    assert "Events of the month" not in text
    assert "Wishlist" not in text
    assert "Planned waterings" not in text
    assert "No events added." in text
    assert "No plants added." in text

#GeneratePDFView for DashboardView
@pytest.mark.django_db
def test_dashboard_pdf_generate_not_logged_fail(client):
    response = client.get(f'/generate-pdf/')
    assert response.status_code == 302

#WishlistRemoveView for DashboardView
@pytest.mark.django_db
def test_wishlist_remove_from_dashboard_logged(client, user_logged,owned_plants,multiple_wishlist):
    client.force_login(user_logged)
    to_remove = multiple_wishlist[0]
    data = { 'plant_id': to_remove.plant.pk, }
    response = client.post('/wishlist-remove/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is True
    assert len(WishList.objects.filter(owner=user_logged)) == 2

#WishlistRemoveView for DashboardView
@pytest.mark.django_db
def test_wishlist_remove_from_dashboard_not_logged_fail(client, user_logged,owned_plants,multiple_wishlist):
    to_remove = multiple_wishlist[0]
    data = { 'plant_id': to_remove.plant.pk, }
    response = client.post('/wishlist-remove/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 302

#WishlistRemoveView for DashboardView
@pytest.mark.django_db
def test_wishlist_remove_from_dashboard_missing_record_fail(client, user_logged,owned_plants,multiple_wishlist):
    client.force_login(user_logged)
    to_remove = multiple_wishlist[0]
    data = { 'plant_id': to_remove.plant.pk, }
    WishList.objects.get(id = to_remove.pk).delete()
    response = client.post('/wishlist-remove/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is False

#WishlistBoughtView for DashboardView
@pytest.mark.django_db
def test_wishlist_bought_from_dashboard_logged(client, user_logged,multiple_wishlist):
    client.force_login(user_logged)
    to_buy = multiple_wishlist[0]
    data = { 'plant_id': to_buy.plant.pk, }
    response = client.post('/wishlist-bought/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is True
    assert OwnedPlants.objects.get(owner=user_logged,plant=to_buy.plant)

#WishlistBoughtView for DashboardView
@pytest.mark.django_db
def test_wishlist_bought_from_dashboard_not_logged_fail(client, user_logged,multiple_wishlist):
    to_buy = multiple_wishlist[0]
    data = { 'plant_id': to_buy.plant.pk, }
    response = client.post('/wishlist-bought/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 302

#WishlistBoughtView for DashboardView
@pytest.mark.django_db
def test_wishlist_bought_from_dashboard_missing_data_fail(client, user_logged,multiple_wishlist):
    client.force_login(user_logged)
    to_buy = multiple_wishlist[0]
    data = { 'plant_id': to_buy.plant.pk, }
    WishList.objects.get(id = to_buy.pk).delete()
    response = client.post('/wishlist-bought/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is False
    assert response.json()['error'] == "No WishList matches the given query."

#RemoveFromOwnedView for DashboardView
@pytest.mark.django_db
def test_wishlist_remove_from_owned_dashboard_logged(client, user_logged,owned_plants):
    client.force_login(user_logged)
    to_remove = owned_plants[0]
    data = { 'plant_id': to_remove.plant.pk, }
    # OwnedPlants.objects.get(owner=user_logged,plant=to_remove.plant).delete()
    response = client.post('/remove-from-owned/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is True
    assert len(OwnedPlants.objects.filter(owner=user_logged)) == 2

#RemoveFromOwnedView for DashboardView
@pytest.mark.django_db
def test_wishlist_remove_from_owned_dashboard_not_logged_fail(client, user_logged,owned_plants):
    to_remove = owned_plants[0]
    data = { 'plant_id': to_remove.plant.pk, }
    # OwnedPlants.objects.get(owner=user_logged,plant=to_remove.plant).delete()
    response = client.post('/remove-from-owned/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 302

#RemoveFromOwnedView for DashboardView
@pytest.mark.django_db
def test_wishlist_remove_from_owned_dashboard_no_owned_fail(client, user_logged,owned_plants):
    client.force_login(user_logged)
    to_remove = owned_plants[0]
    data = { 'plant_id': to_remove.plant.pk, }
    OwnedPlants.objects.get(owner=user_logged,plant=to_remove.plant).delete()
    response = client.post('/remove-from-owned/', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.json()['success'] is False

#OwnedPlantDetailView
@pytest.mark.django_db
def test_owned_plant_logged(client, user_logged,owned_plants):
    client.force_login(user_logged)
    for item in owned_plants:
        response = client.get(f'/my-plants/{item.plant.pk}/')
        assert response.status_code == 200

#OwnedPlantDetailView
@pytest.mark.django_db
def test_owned_plant_not_logged_fail(client, user_logged,owned_plants):
    for item in owned_plants:
        response = client.get(f'/my-plants/{item.plant.pk}/')
        assert response.status_code == 302

#OwnedPlantDetailView
@pytest.mark.django_db
def test_plant_not_owned_fail(client, user_logged):
    client.force_login(user_logged)
    response = client.get(f'/my-plants/35463/')
    assert response.status_code == 404

#OwnedPlantDetailView
@pytest.mark.django_db
def test_no_owned_plants_fail(client, user_logged, owned_plants):
    other_user = User.objects.create_user(username="otheruser", password="otherpass")
    client.force_login(other_user)
    for item in owned_plants:
        response = client.get(f'/my-plants/{item.plant.pk}/')
        assert response.status_code == 404

#AllEventsView
# generate_plotly_chart
# get_watering_differences