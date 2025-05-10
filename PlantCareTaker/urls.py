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
                          DashboardView, RegisterView, AddEventView,  DiagnosePlantView,
                          OwnedPlantDetailView, AddWateringView, UserProfileView, AddCommentView,
                          ChangeWateringFrequencyView, RemoveFromWishlistView,AddToWishlistView,
                          FinishWateringView, MoveWateringView, WishlistRemoveView, AddNoteView,
                          WishlistBoughtView, FinishEventView, CancelEventView, GeneratePDFView,
                          AllEventsView, GenerateWeatherTipView)
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomepageView.as_view(), name="home"),
    path("addplant/", AddPlantView.as_view(), name="addplant"),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('all-events/', AllEventsView.as_view(), name='all_events'),
    path('catalog/',CatalogView.as_view(), name='catalog'),
    path('plants/<int:pk>/', PlantDetailView.as_view(), name='plant-detail'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path("login/",LoginView.as_view(template_name='plants/login.html'),name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path('add-event/', AddEventView.as_view(), name='add-event'),
    path('finish-event/<int:pk>', AddEventView.as_view(), name='finish-event'),
    path('generate-pdf/', GeneratePDFView.as_view(), name='generate-pdf'),
    path('diagnose/', DiagnosePlantView.as_view(), name='diagnose-plant'),
    path('my-plants/<int:pk>/', OwnedPlantDetailView.as_view(), name='my-plants'),
    path('finish-event/', FinishEventView.as_view(), name='finish-event'),
    path('cancel-event/', CancelEventView.as_view(), name='cancel-event'),
    path('add-note/', AddNoteView.as_view(), name='add-note'),
    path('wishlist-remove/', WishlistRemoveView.as_view(), name='wishlist-remove'),
    path('wishlist-bought/', WishlistBoughtView.as_view(), name='wishlist-bought'),
    path('add-watering/', AddWateringView.as_view(), name='add-watering'),
    path('move-watering/', MoveWateringView.as_view(), name='move-watering'),
    path('finish-watering/', FinishWateringView.as_view(), name='finish-watering'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('add-to-wishlist/', AddToWishlistView.as_view(), name='add-to-wishlist'),
    path('remove-from-wishlist/', RemoveFromWishlistView.as_view(), name='remove-from-wishlist'),
    path('change-watering-frequency/',ChangeWateringFrequencyView.as_view(), name='change-watering-frequency'),
    path('add-comment/', AddCommentView.as_view(), name='add-comment'),
    path('generate-plant-pdf/<int:pk>/', views.generate_plant_pdf, name='generate-plant-pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
