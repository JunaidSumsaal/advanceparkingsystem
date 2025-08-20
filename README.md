# AdvanceParkingSystem

AdvanceParkingSystem is a **full-stack smart parking management platform** with a **Django REST Framework backend** and a **React (Tailwind) frontend**.

It integrates **AI-powered parking spot predictions**, **real-time notifications**, and **role-based dashboards** for Drivers, Attendants, and Providers.



## Features

### Authentication & User Roles

* Custom user model with roles: **Driver**, **Attendant**, **Provider**, **Admin**.
* JWT-based authentication.
* Advanced audit logging for all actions.

### Parking Management

* Facility & spot management (public/private).
* Spot availability logs and booking history.
* Soft delete/restore for facilities and spots.

### Booking & Navigation

* Real-time spot booking and cancellation.
* Booking prevention for unavailable/self-owned spots.
* Google Maps integration for navigation.

### AI-Powered Predictions

* Random Forest–based **availability predictor**.
* Features include time, spot type, demand ratios, and active bookings.
* Training command + evaluation metrics (AUC, Precision, Brier).

### Notifications

* Push subscriptions via Web Push API.
* Email preferences for users.
* Types: spot availability, booking reminders, general alerts.

### Dashboards

* **Driver Dashboard** – Nearby spots, bookings, navigation.
* **Attendant Dashboard** – Facility/spot oversight.
* **Provider Dashboard** – Occupancy, revenue, prediction reports.



## Project Structure

```bash
advanceparkingsystem/
│── backend/                 # Django backend (REST API + ML)
│   ├── accounts/            # Custom user model & auth
│   ├── parking/             # Facilities, spots, bookings, predictions
│   ├── notifications/       # Push/email notification system
│   ├── dashboard/           # Role-based dashboards
│   ├── core/                # Settings, metrics, utilities
│   └── manage.py
│
│── frontend/                # React + Tailwind frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Page-level views
│   │   ├── hooks/           # Custom hooks (auth, API)
│   │   └── App.js
│   └── package.json
│
└── README.md
```



## Backend Setup (Django)

### Prerequisites

* Python **3.10+**
* Django **4.x**
* PostgreSQL or SQLite

### Steps

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Seed database with demo data
python manage.py seed_data

# Run backend server
python manage.py runserver
```

### Train the Prediction Model

```bash
python manage.py train_spot_predictor
```



## Frontend Setup (React + Tailwind)

### Prerequisites

* Node.js **16+**
* npm or yarn

### Steps

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The React app runs by default at:
**[http://localhost:5173](http://localhost:5173)**



## Development

### Superuser for backend

```bash
python manage.py createsuperuser
```

### Admin panel

[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

### API root

[http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)



## Pending Features

* [ ] Dynamic pricing engine.
* [ ] Background push notification delivery (Celery).
* [ ] In-app WebSocket notifications.
* [ ] Export reports (CSV/Excel).
* [ ] Admin dashboards for analytics.
* [ ] Dockerized AI training pipeline.



## 📜 License

MIT License – free to use, modify, and distribute.



Would you like me to also include **frontend/backend integration instructions** (e.g., how React calls the Django API with Axios + JWT) so developers don’t get stuck wiring them together?
