from django.contrib import admin

from plants.models import Plant, Event, SoilType, SoilIngredient, PlantDetailComments, OwnedPlants, WishList, UserNotes, \
    Watering, AIRating, PlantTips,UserLocation
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User

admin.site.register(Event)
admin.site.register(SoilType)
admin.site.register(SoilIngredient)
admin.site.register(PlantDetailComments)
admin.site.register(OwnedPlants)
admin.site.register(WishList)
admin.site.register(AIRating)
admin.site.register(PlantTips)

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    readonly_fields = ('id',)
    fieldsets = (
        ('Admin',{'fields':('id','image','name')}),
        ('Requirements', {'fields': ('soil', 'light','watering_frequency')}),
        ('Description',{'fields': ('description',)}),
    )
    ordering = ('name','id')

@admin.register(UserNotes)
class UserNotesAdmin(admin.ModelAdmin):
        list_display = ('date', 'user')
        readonly_fields = ('id','date')
        fieldsets = (
            ('Admin', {'fields': ('id', 'user', 'plant')}),
            ('Details', {'fields': ('note', 'date','type')}),
        )
        ordering = ('date', 'user')

@admin.register(Watering)
class WateringAdmin(admin.ModelAdmin):
        list_display = ('date', 'user')
        readonly_fields = ('id','date')
        fields=('id','date','user','plant')
        ordering = ('date', 'user')

class UserLocationInline(admin.StackedInline):  # albo TabularInline
    model = UserLocation
    extra = 0

class UserAdmin(DefaultUserAdmin):
    inlines = [UserLocationInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)