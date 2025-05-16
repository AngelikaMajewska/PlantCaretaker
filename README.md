# 🌿 PlantCaretaker

**PlantCaretaker** is a web application designed to help users manage and monitor their plant care routines. It allows users to add plants, track watering schedules, and receive AI-powered diagnoses based on plant images.

## Features

- Add plants from the catalog to your owned list
- Manage the care for each of your plants
  - Diagnose plant health from images (Grok API, for users with permission)
  - Track watering and fertilizing schedules
  - Adjust the watering frequency
- Get general tips and tips based on your location
- Plan all your plant-related tasks with the help of a calendar and event list
- Wishlist functionality for logged-in users
- Find the plant with just image (Grok API, for users with permission)
- Add new plants to the catalog (admin functionality)
  - Download the PDF with all events planned for current month and prognosed waterings for each plant


## Technologies Used

- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **AI Integration**: Utilizes external AI services for image-based plant diagnosis
- **External APIs**: Grok Vision for image analysis, OpenWeather for location specific tips

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/AngelikaMajewska/PlantCaretaker.git
   cd PlantCaretaker

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install the required packages**:
   
   ```bash
   pip install -r requirements.txt

4. **Apply migrations**:

    ```bash
   python manage.py migrate

5. **Run the development server**:

   ```bash
   python manage.py runserver

6.	**Access the application**:

    Open your browser and go to http://127.0.0.1:8000/

### Running Tests

  To run tests using pytest:
  
  ```bash
  pytest
  ```
  
  Make sure all test dependencies are installed.


## Project Structure
```
PlantCaretaker/
├── media/                      # Uploaded media files (e.g., plant images)
│   └── plant_images/
├── plants/                     # Main Django app
│   ├── migrations/             # Database migrations
│   ├── static/                 # Static files (CSS, JS, images)
│   ├── templates/              # HTML templates
│   ├── admin.py                # Admin panel registration
│   ├── apps.py                 # App configuration
│   ├── models.py               # Django models
│   ├── tests.py                # Unit tests
│   └── views.py                # View logic
├── PlantCaretaker/             # Django project configuration
│   ├── settings.py             # Project settings
│   ├── urls.py                 # Main URL configuration
│   └── wsgi.py                 # WSGI entry point for production
├── manage.py                   # Django's command-line tool
├── requirements.txt            # Python dependency list
└── README.md                   # Project documentation
```

## Screenshots

### Dashboard
<img width="1165" alt="Zrzut ekranu 2025-05-16 o 18 12 55" src="https://github.com/user-attachments/assets/1faf9f58-9554-4aa6-b0f4-de283c6d3a51" />

### Catalog
<img width="1066" alt="Zrzut ekranu 2025-05-16 o 18 13 39" src="https://github.com/user-attachments/assets/8768057f-47ab-4840-a5b5-aa15e8aa9f26" />

### Calendar
<img width="1302" alt="Zrzut ekranu 2025-05-16 o 18 14 28" src="https://github.com/user-attachments/assets/90a56de0-e239-4f1f-b41e-9047aae0640b" />

### Add plant
<img width="560" alt="image" src="https://github.com/user-attachments/assets/2793f356-ae28-4d68-93cf-6f16631beb8a" />

### Plant catalog view
<img width="1080" alt="image" src="https://github.com/user-attachments/assets/d5276b3f-b29a-413c-86b7-cc0e09bd7409" />

### Owned plant view
<img width="1109" alt="image" src="https://github.com/user-attachments/assets/c815bdc6-9a2b-442c-9ce5-b346350ac0ca" />

#### AI diagnosis for users with permission
<img width="1022" alt="image" src="https://github.com/user-attachments/assets/f810f284-2332-4636-98ba-995077c57a28" />






  
