"""
URL configuration for PlantCareTaker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from plants import views
from plants.views import (HomepageView, AddPlantView, CalendarView, CatalogView, PlantDetailView,
                          DashboardView, RegisterView,AddEventView,generate_pdf,DiagnosePlantView,
                          OwnedPlantDetailView, AddWateringView, UserProfileView)
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomepageView.as_view(), name="home"),
    path("addplant/", AddPlantView.as_view(), name="addplant"),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('all-events/', views.all_events, name='all_events'),
    path('catalog/',CatalogView.as_view(), name='catalog'),
    path('plants/<int:pk>/', PlantDetailView.as_view(), name='plant-detail'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path("login/",LoginView.as_view(template_name='plants/login.html'),name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path('add-event/', AddEventView.as_view(), name='add-event'),
    path('finish-event/<int:pk>', AddEventView.as_view(), name='finish-event'),
    path('generate-pdf/', generate_pdf, name='generate-pdf'),
    path('diagnose/', DiagnosePlantView.as_view(), name='diagnose-plant'),
    path('my-plants/<int:pk>/', OwnedPlantDetailView.as_view(), name='my-plants'),
    path('finish-event/', views.finish_event, name='finish-event'),
    path('cancel-event/', views.cancel_event, name='cancel-event'),
    path('add-note/', views.add_note, name='add-note'),
    path('wishlist-remove/', views.wishlist_remove, name='wishlist-remove'),
    path('wishlist-bought/', views.wishlist_bought, name='wishlist-bought'),
    path('add-watering/', AddWateringView.as_view(), name='add-watering'),
    path('move-watering/', views.move_watering, name='move-watering'),
    path('finish-watering/', views.finish_watering, name='finish-watering'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add-to-wishlist'),
    path('remove-from-wishlist/', views.remove_from_wishlist, name='remove-from-wishlist'),
    path('change-watering-frequency/',views.change_watering_frequency, name='change-watering-frequency'),
    path('add-comment/', views.add_comment, name='add-comment'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
