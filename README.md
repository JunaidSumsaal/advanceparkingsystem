# AdvanceParkingSystem

AdvanceParkingSystem is a **full-stack smart parking management platform** with a **Django REST Framework backend** and a **React (Vite + Tailwind) frontend**.

It integrates **AI-powered parking spot predictions**, **real-time notifications**, and **role-based dashboards** for Drivers, Attendants, and Providers.
This system is designed to streamline parking operations, enhance user experience, and leverage machine learning for future availability predictions.

## Features

### Authentication & User Roles

* JWT authentication with refresh tokens.
* Roles: **Driver**, **Attendant**, **Provider**, **Admin**.
* Advanced audit logging (all user actions tracked).

### Parking Management

* Facility & spot management.
* Soft delete & restore (archival mode).
* Booking history & real-time spot availability.

### Booking & Navigation

* One-click booking & cancellation.
* Google Maps integration for navigation.
* Prevent self-booking (providers can’t book their own spots).

### AI-Powered Predictions

* Random Forest model for **future availability**.
* Training + evaluation (`AUC`, `Brier`, `Precision`).
* Per-spot prediction logging.

### Notifications

* Push API subscriptions.
* Email preferences per user.
* Notification templates (availability, booking reminders, alerts).

### Dashboards

* **Driver Dashboard** → Nearby spots, bookings, navigation.
* **Attendant Dashboard** → Facility/spot oversight.
* **Provider Dashboard** → Revenue, occupancy, AI reports.
* **Admin Dashboard** → User management, analytics, system health.

### Metrics & Analytics

* System health metrics (uptime, response times).
* User activity tracking (logins, bookings).
* Spot usage analytics (occupancy rates, peak times).

## Project Structure

```bash
advanceparkingsystem/
│── backend/                 # Django backend (REST API + ML)
│   ├── accounts/            # Authentication + roles
│   ├── parking/             # Facilities, spots, bookings, predictions
│   ├── notifications/       # Push/email notifications
│   ├── dashboard/           # Role-based dashboards
│   ├── core/                # Settings, utils, metrics
│   └── manage.py
│
│── frontend/                # React + Vite + Tailwind frontend
│   ├── src/
│   │   ├── api/             # Axios API clients
│   │   ├── components/      # UI components
│   │   ├── pages/           # Page views
│   │   ├── hooks/           # Auth & data fetching hooks
│   │   └── App.jsx
│   └── package.json
│
└── README.md
```


## Backend Setup (Django)

### Prerequisites

* Python **3.10+**
* Django **4.x**
* PostgreSQL or SQLite

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

# Run backend
python manage.py runserver
```

Backend runs on **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

## Train the Prediction Model

```bash
# Train the AI model for parking spot predictions
# This will create a Random Forest model and save it to the database
# Ensure you have the necessary data in your database before running this
python manage.py train_spot_predictor
```

## Frontend Setup (React + Vite + Tailwind)

### Prerequisites

* Node.js **16+**
* npm or yarn

```bash
cd frontend

# Install dependencies
npm install

# Run frontend (Vite dev server)
npm run dev
```

Frontend runs on **[http://localhost:5173/](http://localhost:5173/)**


## Connecting Frontend & Backend

### 1. Configure API base URL

Create **`frontend/src/api/axios.js`**

```javascript
import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api/",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### 2. Example Auth API

**`frontend/src/api/auth.js`**

```javascript
import api from "./axios";
import Cookies from "js-cookie";

export const login = async (username, password) => {
  const response = await api.post("token/", { username, password });
  if (response.data.access) {
    Cookies.set("access", response.data.access);
    Cookies.set("refresh", response.data.refresh);
  }
  return response.data;
};

export const logout = () => {
  Cookies.removeItem("access");
  Cookies.removeItem("refresh");
};
```

### 3. Fetch Example (Nearby Spots)

```javascript
import api from "./axios";

export const getNearbySpots = async (lat, lng, radius = 2) => {
  const res = await api.get("parking/nearby/", {
    params: { lat, lng, radius },
  });
  return res.data;
};
```



### 4. Usage in a React Component

```jsx
import React, { useEffect, useState } from "react";
import { getNearbySpots } from "../api/parking";

export default function NearbySpots() {
  const [spots, setSpots] = useState([]);

  useEffect(() => {
    navigator.geolocation.getCurrentPosition((pos) => {
      getNearbySpots(pos.coords.latitude, pos.coords.longitude).then(setSpots);
    });
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold">Nearby Spots</h2>
      <ul>
        {spots.map((s) => (
          <li key={s.id}>
            {s.name} — {s.latitude}, {s.longitude}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## Environment Configuration

### Backend (`backend/.env`)

Create a `.env` file inside the **backend/** folder:

```ini
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database (Postgres recommended)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=advanceparking
DB_USER=advanceparking_user
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# JWT Settings
ACCESS_TOKEN_LIFETIME=60          # minutes
REFRESH_TOKEN_LIFETIME=1          # days

# Email (for notifications & password reset)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=youremail@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# Push Notifications (WebPush VAPID keys)
VAPID_PUBLIC_KEY=your-public-key
VAPID_PRIVATE_KEY=your-private-key
VAPID_ADMIN_EMAIL=admin@advanceparking.com

# CORS (to allow frontend requests)
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Load it in **`backend/core/settings.py`** using `django-environ`:

```python
import environ
import os

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": env("DB_NAME", default=os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": env("DB_USER", default=""),
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default=""),
        "PORT": env("DB_PORT", default=""),
    }
}
```

### Frontend (`frontend/.env`)

Create a `.env` file inside the **frontend/** folder:

```ini
# API URL (Backend Django)
VITE_API_BASE_URL=http://127.0.0.1:8000/api

# Google Maps API (for navigation links)
VITE_GOOGLE_MAPS_KEY=your-google-maps-key

# Push Notifications
VITE_VAPID_PUBLIC_KEY=your-public-key
```

Access in **React Vite** like this:

```javascript
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

fetch(`${apiBaseUrl}/parking/nearby/`)
  .then((res) => res.json())
  .then(console.log);
```


### Generating VAPID Keys for Push Notifications

Run this in Django shell:

```bash
pip install pywebpush
python manage.py shell
```

```python
from pywebpush import generate_vapid_keys
print(generate_vapid_keys())
```

This will give you:

```txt
publicKey:  "BNxxxxxxx"
privateKey: "kxxxxxxx"
```

Place them in `.env` for backend + frontend.

## Pending Features

* [ ] Dynamic pricing engine.
* [ ] Background push notification delivery (Celery).
* [ ] WebSocket-based in-app notifications.
* [ ] Export reports (CSV/Excel).
* [ ] Admin dashboards for analytics.
* [ ] Dockerized AI training pipeline.

## License

MIT License – free to use, modify, and distribute.
