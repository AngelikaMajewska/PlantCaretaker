import json
import base64
import os

import requests
from datetime import timedelta, date, datetime
import plotly.graph_objs as go
import plotly.offline as opy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from weasyprint import HTML
from collections import defaultdict

from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, DetailView, CreateView, View, UpdateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.http import HttpResponse

from .models import Event, Plant, OwnedPlants, WishList, UserNotes, AIRating, Watering, PlantTips, UserLocation, \
    PlantDetailComments
from .forms import PlantForm, CustomUserCreationForm, EventForm, WateringForm, UserForm, UserLocationForm
from django.conf import settings

api_key = settings.WEATHER_API_KEY

def generate_weather_tip(city):
    API_KEY = api_key
    print(city)
    CITY = city
    url = f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric'

    response = requests.get(url)
    data = response.json()
    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    weather = data['weather'][0]['main'].lower()

    tip = "It's a good day for routine watering."

    if temperature > 28:
        tip = "It's very hot – consider earlier watering, preferably in the morning or in the evening, to avoid evaporation."
    elif temperature < 5:
        tip = "It's cold – limit the watering, plants can rest."
    elif "rain" in weather:
        tip = "It's raining – if you keep your plants outside, they might not need additional watering."
    elif humidity < 30:
        tip = "Low humidity – plants might use some extra misting."

    return {
        "tip": tip,
        "date": datetime.today().date(),
        "temperature": temperature,
        "weather": weather,
        "humidity": humidity,
        "city": city
    }

class HomepageView(TemplateView):
    template_name = ('plants/home.html')

class AddPlantView(FormView):
    template_name = 'plants/add_plant.html'
    form_class = PlantForm
    success_url = '/addplant/'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class CalendarView(TemplateView):
    template_name = 'plants/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # tips=generate_random_tips()
        context['event_form'] = EventForm(user=user)
        context['events'] = Event.objects.filter(user=user, is_finished=False).order_by('date')
        return context


class AllEventsView(View):
    def get(self, request, *args, **kwargs):
        events = Event.objects.filter(
            user=request.user,
            is_finished=False
        ).select_related('plant').order_by('date')

        event_list = []
        for event in events:
            event_list.append({
                'title': event.name,
                'plant': {
                    'id': event.plant.id,
                    'name': event.plant.name,
                } if event.plant else None,
                'start': event.date.strftime("%Y-%m-%d"),
                'description': event.description,
            })

        return JsonResponse(event_list, safe=False)

class CatalogView(TemplateView):
    template_name = 'plants/catalog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plants'] = Plant.objects.all().order_by('name')
        wishlist = WishList.objects.filter(owner_id=self.request.user.id)
        plant_ids = wishlist.values_list('plant_id', flat=True)
        list_of_ids = list(plant_ids)
        context['wishlist'] = list_of_ids
        owned = OwnedPlants.objects.filter(owner_id=self.request.user.id)
        owned_ids = owned.values_list('plant_id', flat=True)
        list_of_owned_ids = list(owned_ids)
        context['owned_plants'] = list_of_owned_ids
        return context

class PlantDetailView(DetailView):
    model = Plant
    template_name = 'plants/plant_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plant = self.get_object()
        comments_list = PlantDetailComments.objects.filter(plant=plant).select_related('user').order_by('-date')

        paginator = Paginator(comments_list, 10)  # 10 komentarzy na stronę
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['plant'] = plant
        context['page_obj'] = page_obj
        return context

# def generate_random_tips():
#     try:
#         prompt = "Generate 3 random tips for houseplant care. I want it in HTML with list only, no header etc. Limit yourself to 200 words."
#         api_key = os.environ.get("XAI_API_KEY")
#
#         if not api_key:
#             return JsonResponse({'success': False, 'error': "API key not found in environment variables."}, status=500)
#
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {api_key}"
#         }
#
#         payload = {
#             "model": "grok-2-vision-1212",
#             "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
#         }
#
#         response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload)
#
#         if response.status_code == 200:
#             result = response.json()["choices"][0]["message"]["content"]
#             print(result)
#             return  result
#         else:
#             return "No tips for today"
#
#     except Exception as e:
#         return "Error"

class DashboardView(TemplateView):
    template_name = 'plants/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # tips=generate_random_tips()
        tips = PlantTips.objects.all().order_by('?')[:2]
        context['tips'] = tips
        context['watering_form'] = WateringForm(user=user)
        owned_plants = OwnedPlants.objects.filter(owner=user).select_related('plant')
        context['owned_plants'] = owned_plants

        owned = []
        for plant in owned_plants:
            owned.append(plant.plant.id)
        last_waterings = []
        for plantid in owned:
            last = Watering.objects.filter(plant_id = int(plantid), user_id = self.request.user.id).order_by('-next_watering').first()
            last_waterings.append(last)
        sorted_waterings = sorted([w for w in last_waterings if w], key=lambda w: w.next_watering)
        context['waterings'] = sorted_waterings

        context['wishlist'] = WishList.objects.filter(owner=user).select_related('plant')
        location=UserLocation.objects.get(user=self.request.user)
        weather_tip = generate_weather_tip(location.city)
        context['weather_tip'] = weather_tip
        return context

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get('form_type')

        if form_type == 'event':
            form = EventForm(request.POST, user=request.user)
            if form.is_valid():
                event = form.save(commit=False)
                event.user = self.request.user
                event.save()
                return redirect('dashboard')
            else:
                context = self.get_context_data()
                context['event_form'] = form
                return self.render_to_response(context)

        elif form_type == 'watering':
            form = WateringForm(request.POST, user=request.user)
            if form.is_valid():
                watering = form.save(commit=False)
                watering.user = request.user
                if not watering.next_watering:
                    watering.next_watering = watering.date + timedelta(days=watering.plant.watering_frequency)
                watering.save()
                return redirect('dashboard')
            else:
                context = self.get_context_data()
                context['watering_form'] = form
                return self.render_to_response(context)

class RegisterView(CreateView):
    template_name = 'plants/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

class AddEventView(View):
    def post(self, request, *args, **kwargs):
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            return JsonResponse({'success': True})
        else:
            errors = form.errors.get_json_data()
            error_list = [v[0]['message'] for k, v in errors.items()]
            return JsonResponse({'success': False, 'errors': error_list})

class AddWateringView(View):
    def post(self, request, *args, **kwargs):
        form = WateringForm(request.POST, user=request.user)
        if form.is_valid():
            watering = form.save(commit=False)
            watering.user = request.user
            watering.save()
            return JsonResponse({'success': True})
        else:
            errors = form.errors.get_json_data()
            error_list = [v[0]['message'] for v in errors.values()]
            print('Form errors:', error_list)  # log do konsoli serwera
            return JsonResponse({'success': False, 'errors': error_list}, status=400)

class GeneratePDFView(View):
    def get(self, request, *args, **kwargs):
        this_month = datetime.today().month

        events = Event.objects.filter(
            user=request.user,
            is_finished=False,
            date__month=this_month
        ).select_related('plant').order_by('date')

        wishlist = WishList.objects.filter(
            owner=request.user
        ).select_related('plant')

        owned_plants = OwnedPlants.objects.filter(
            owner=request.user
        ).select_related('plant')

        owned = [plant.plant.id for plant in owned_plants]

        last_waterings = []
        for plant_id in owned:
            last = Watering.objects.filter(
                plant_id=plant_id,
                user_id=request.user.id
            ).order_by('-next_watering').first()
            if last:
                last_waterings.append(last)

        waterings_dict = {}
        for item in last_waterings:
            plant_name = item.plant.name
            frequency = item.plant.watering_frequency
            start_date = item.next_watering
            future_dates = [
                start_date + timedelta(days=frequency * i)
                for i in range(1, 15)
                if (start_date + timedelta(days=frequency * i)).month == this_month
            ]
            waterings_dict[plant_name] = future_dates

        sorted_waterings = sorted(
            [(plant, dates) for plant, dates in waterings_dict.items() if dates],
            key=lambda x: x[1][0]
        )

        grouped_by_day = defaultdict(list)
        for plant_name, dates in sorted_waterings:
            for date in dates:
                key = date.strftime('%B %d')
                grouped_by_day[key].append(plant_name)

        grouped_by_day = dict(sorted(
            grouped_by_day.items(),
            key=lambda x: datetime.strptime(x[0], "%B %d")
        ))

        context = {
            'events': events,
            'wishlist': wishlist,
            'grouped_by_day': grouped_by_day,
        }

        html_string = render_to_string('plants/pdf_template.html', context)
        html = HTML(string=html_string)
        pdf_file = html.write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="month_planner.pdf"'
        return response

@method_decorator(csrf_exempt, name='dispatch')
class DiagnosePlantView(View):
    def post(self, request):
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image provided'}, status=400)

        try:
            # Get file from request
            file = request.FILES.get('image')
            plant_id=request.POST.get('plant_id')
            plant = Plant.objects.get(pk=plant_id)
            prompt = f"The photo is of {plant.name}. Rate the condition of the plant in this photo on a scale of 1-5, return a rating and provide possible causes of problems. Do not use markdown, limit yourself to 100 words."

            # Read image data
            image_data = file.read()

            # Encode to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')

            # Get file format from filename
            image_format = file.name.rsplit('.', 1)[1].lower() if '.' in file.name else 'jpeg'

            # Get API key - preferably from environment variables
            api_key = os.environ.get("XAI_API_KEY", "xai-KEY")

            # Call Vision API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            payload = {
                "model": "grok-2-vision-1212",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image_format};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            }

            response = requests.post("https://api.x.ai/v1/chat/completions",headers=headers,json=payload)
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]

                print(result)
                AIRating.objects.create(plant=plant,user=self.request.user,note=result)
                return JsonResponse({ 'success': True, 'diagnosis': result})
            else:
                return JsonResponse({'success': False,'error': f"API Error: {response.status_code}",'details': response.text }, status=500)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

def generate_plotly_chart(labels, values):
    trace = go.Scatter(
        x=labels,
        y=values,
        mode='lines+markers',
        name='Rating',
        line=dict(color='rgba(194, 209, 128, 1)', width=3, dash='solid'),
        marker=dict(size=8, color='rgba(160, 166, 98, 1)', symbol='circle'),
        text = [f"{label} Rating: {value}/5" for label, value in zip(labels, values)],
        hoverinfo = 'text'
    )

    layout = go.Layout(
        xaxis=dict(
            title='Date',
            tickangle=-45,
            gridcolor='rgba(237, 245, 201, 1)',
            zeroline=False
        ),
        yaxis=dict(
            title='Rating',
            gridcolor='lightgrey',
            zeroline=False,
            dtick=1,
        ),
        plot_bgcolor='rgba(242, 246, 226, 1)',  # Jasne tło
        paper_bgcolor='white',
        font=dict(family='Verdana', size=12, color='rgba(86, 89, 0, 1)'),
        margin=dict(l=50, r=50, t=80, b=100),
        width=500,
        height=300
    )

    fig = go.Figure(data=[trace], layout=layout)
    chart_html = opy.plot(fig, auto_open=False, output_type='div')
    return chart_html

def get_watering_differences(plant_id):
    waterings = Watering.objects.filter(plant_id=plant_id).order_by('date')

    dates = [w.date for w in waterings]
    fertilisers = [w.fertiliser for w in waterings]

    diffs = []
    marker_colors = []
    for i in range(1, len(dates)):
        delta = (dates[i] - dates[i - 1]).days
        diffs.append(delta)
        # Kolor zależny od fertiliser
        if fertilisers[i]:  # current watering
            marker_colors.append('rgba(86, 89, 0, 1)')  # np. pomarańczowy dla nawożenia
        else:
            marker_colors.append('rgba(160, 166, 98, 1)')  # zielony dla zwykłego podlewania

    # Oś X: daty bez pierwszej (bo różnice są między parą)
    x = dates[1:]
    y = diffs

    trace = go.Scatter(
        x=x,
        y=y,
        mode='lines+markers',
        name='Days between registered waterings',
        line=dict(color='rgba(194, 209, 128, 1)', width=3, dash='solid'),
        marker=dict(size=8, color=marker_colors, symbol='circle'),
        text=[f"{date} - {days} days (Fertilizer: {'Yes' if fert else 'No'})" for date, days, fert in
              zip(x, y, fertilisers[1:])],
        hoverinfo='text'
    )

    layout = go.Layout(
        xaxis=dict(
            title='Date',
            tickangle=-45,
            gridcolor='rgba(242, 246, 226, 1)',
            zeroline=False
        ),
        yaxis=dict(
            title='Days since last watering',
            gridcolor='lightgrey',
            zeroline=False,
            dtick=0.5
        ),
        plot_bgcolor='rgba(242, 246, 226, 1)',
        paper_bgcolor='white',
        font=dict(family='Verdana', size=12, color='rgba(86, 89, 0, 1)'),
        margin=dict(l=30, r=30, t=30, b=30),
        width=500,
        height=300
    )

    fig = go.Figure(data=[trace], layout=layout)
    chart_html = opy.plot(fig, auto_open=False, output_type='div')
    return chart_html

class OwnedPlantDetailView(TemplateView):
    template_name = 'plants/owned_plants.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plant_id = self.kwargs['pk']
        plant = Plant.objects.get(pk=plant_id)
        context['plant'] = plant
        user_notes = UserNotes.objects.filter(user_id=self.request.user.id, plant_id = plant_id).order_by('-date')
        context['user_notes'] = user_notes
        ai_rating = AIRating.objects.filter(user_id=self.request.user.id, plant = plant).order_by('date')
        labels = [r.date.strftime('%d.%m.%Y') for r in ai_rating]
        values = [r.rating for r in ai_rating]
        ai_rating = AIRating.objects.filter(user_id=self.request.user.id, plant=plant).order_by('-date')
        context['ai_rating'] = ai_rating
        context['plotly_chart'] = generate_plotly_chart(labels, values)
        context['watering_chart'] = get_watering_differences(plant_id)
        watering = Watering.objects.filter(user_id=self.request.user.id, plant_id = plant_id).order_by('-date')
        last_watering=watering.order_by('-date').first()
        context['last_watering'] = last_watering
        if not watering.order_by('-date').first() :
            next_watering=date.today()
        else:
            next_watering=last_watering.next_watering
            context['next_watering'] = next_watering
        context['waterings'] = watering
        watering_frequency = OwnedPlants.objects.get(owner_id=self.request.user.id, plant_id = plant_id).owner_watering_frequency
        context['watering_frequency'] = watering_frequency
        return context
class FinishEventView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            event_id = data.get("event_id")
            event = Event.objects.get(id=event_id)
            event.is_finished = True
            event.save()
            return JsonResponse({"success": True})
        except Event.DoesNotExist:
            return JsonResponse({"success": False, "error": "Event doesn't exist"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"success": False, "error": "Bad request"})
class CancelEventView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            event_id = data.get("event_id")
            event = Event.objects.get(id=event_id)
            event.delete()
            return JsonResponse({"success": True})
        except Event.DoesNotExist:
            return JsonResponse({"success": False, "error": "Event doesn't exist"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"success": False, "error": "Bad request"})
class AddNoteView(View):
    def post(self, request, *args, **kwargs):
        try:
            plant_id = request.POST.get("plant_id")
            user_id = request.POST.get("user_id")
            note_text = request.POST.get("note")

            if not note_text:
                return JsonResponse({"success": False, "error": "Note is empty"})

            UserNotes.objects.create(user_id=user_id, plant_id=plant_id, note=note_text)
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"success": False, "error": "Invalid request method"})
class WishlistRemoveView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            plant_id = data.get("plant_id")
            owner_id = request.user.id

            wishlist_plant = WishList.objects.get(plant_id=plant_id, owner_id=owner_id)
            wishlist_plant.delete()
            return JsonResponse({"success": True})
        except WishList.DoesNotExist:
            return JsonResponse({"success": False, "error": "Plant not found on wishlist"})
        except Exception:
            return JsonResponse({"success": False, "error": "Some error occurred"})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"success": False, "error": "Bad request"})
class WishlistBoughtView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            plant_id = data.get("plant_id")
            owner_id = request.user.id

            wishlist_plant = WishList.objects.get(plant_id=plant_id, owner_id=owner_id)
            owned, created = OwnedPlants.objects.get_or_create(plant_id=plant_id, owner_id=owner_id)
            wishlist_plant.delete()
            return JsonResponse({"success": True, "created": created})

        except WishList.DoesNotExist:
            return JsonResponse({"success": False, "error": "Plant not found on wishlist."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"success": False, "error": "Invalid request method."})
class MoveWateringView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            watering_id = data.get("watering_id")
            days = int(data.get("days"))

            watering = Watering.objects.get(id=watering_id)
            watering.next_watering += timedelta(days=days)
            watering.save()
            return JsonResponse({"success": True})

        except Watering.DoesNotExist:
            return JsonResponse({"success": False, "error": "Watering not found on the list."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"success": False, "error": "Invalid request method."})
class FinishWateringView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            watering_id = data.get("watering_id")
            fertilizer = data.get("fertilizer")
            fertilizer = True if fertilizer == "True" else False

            watering = Watering.objects.get(id=watering_id)
            user_id = request.user.id
            plant_id = watering.plant.id

            user_plant = OwnedPlants.objects.get(owner=request.user, plant=plant_id)
            user_watering_frequency = user_plant.owner_watering_frequency

            new_watering = Watering.objects.create(
                user_id=user_id,
                plant_id=plant_id,
                date=date.today(),
                fertiliser=fertilizer,
                next_watering=(date.today() + timedelta(days=user_watering_frequency))
            )

            return JsonResponse({"success": True})

        except Watering.DoesNotExist:
            return JsonResponse({"success": False, "error": "Watering not found on the list."})
        except OwnedPlants.DoesNotExist:
            return JsonResponse({"success": False, "error": "User does not own this plant."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"success": False, "error": "Invalid request method."})
class UserProfileView(LoginRequiredMixin, View):
    template_name = 'plants/user_profile.html'

    def get(self, request, *args, **kwargs):
        user_form = UserForm(instance=request.user)
        location, _ = UserLocation.objects.get_or_create(user=request.user)
        location_form = UserLocationForm(instance=location)
        return render(request, self.template_name, {
            'user_form': user_form,
            'location_form': location_form
        })

    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST, instance=request.user)
        location, _ = UserLocation.objects.get_or_create(user=request.user)
        location_form = UserLocationForm(request.POST, instance=location)

        if user_form.is_valid() and location_form.is_valid():
            user_form.save()
            location_form.save()
            return redirect('profile')  # lub inna nazwa URL

        return render(request, self.template_name, {
            'user_form': user_form,
            'location_form': location_form
        })
class AddToWishlistView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            plant_id = data.get("plant_id")
            owner_id = data.get("owner_id")

            if WishList.objects.filter(owner_id=owner_id, plant_id=plant_id).exists():
                return JsonResponse({"success": False, "error": "Plant already in wishlist."})

            WishList.objects.create(plant_id=plant_id, owner_id=owner_id)
            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"success": False, "error": "Invalid request method."})
class RemoveFromWishlistView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            plant_id = data.get("plant_id")
            owner_id = data.get("owner_id")

            if WishList.objects.filter(owner_id=owner_id, plant_id=plant_id).exists():
                record = WishList.objects.get(owner_id=owner_id, plant_id=plant_id)
                record.delete()
                return JsonResponse({"success": True})

            return JsonResponse({"success": False, "error": "Plant not in the wishlist."})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"success": False, "error": "Invalid request method."})
class ChangeWateringFrequencyView(View):
    def post(self, request, *args, **kwargs):
        try:
            plant_id = request.POST.get("plant_id")
            owner_id = request.POST.get("owner_id")
            frequency = request.POST.get("frequency")

            if OwnedPlants.objects.filter(owner_id=owner_id, plant_id=plant_id).exists():
                record = OwnedPlants.objects.get(owner_id=owner_id, plant_id=plant_id)
                record.owner_watering_frequency = frequency
                record.save()
                return JsonResponse({"success": True})

            return JsonResponse({"success": False, "error": "Operation unsuccessful."})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"success": False, "error": "Invalid request method."})
class AddCommentView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            plant_id = data.get("plant_id")
            user_id = data.get("user_id")
            comment = data.get("comment")

            new_comment = PlantDetailComments.objects.create(
                plant_id=plant_id,
                user_id=user_id,
                comment=comment
            )
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    def get(self, request, *args, **kwargs):
        return JsonResponse({"success": False, "error": "Invalid request method."})

def generate_plant_pdf(request, pk):
    plant_id = pk
    plant = Plant.objects.get(pk=plant_id)
    plant_name = plant.name

    context = {
        'plant': plant,
    }

    html_string = render_to_string('plants/pdf_plant_detail_template.html', context)
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{plant_name}_detail.pdf"'
    return response
