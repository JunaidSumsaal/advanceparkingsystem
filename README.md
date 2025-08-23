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

## Seeded Credentials for the Project

Below are the **default credentials** for the **Admin**, **Provider**, **Attendant**, and **Driver** users seeded into the system.
You can use these to log in and test the application.

**Note**: The Following seeds are used for sumulations to test and predict nearby routes for **drivers(customers)**.

### 1. **Admin Credentials**

#### Show Admin Credentials

* **Username**: `admin1`
* **Email**: `admin1@example.com`
* **Password**: `password123`


### 2. **Provider Credentials**

#### Show Provider Credentials

* **Username**: `provider1`
* **Email**: `provider1@example.com`
* **Password**: `password123`

> **Note**: You can create multiple **Providers** (e.g., `provider2`, `provider3`, etc. up-to 10), with unique credentials generated for each one.


### 3. **Attendant Credentials**

#### Show Attendant Credentials

* **Username**: `attendant1`
* **Email**: `attendant1@example.com`
* **Password**: `password123`

> **Note**: Multiple **Attendants** are available, such as `attendant2`, `attendant3`, etc., for testing up-to 40.


### 4. **Driver Credentials**

#### Show Driver Credentials

* **Username**: `driver1`
* **Email**: `driver1@example.com`
* **Password**: `password123`

> **Note**: Multiple **Drivers** are available (e.g., `driver2`, `driver3`, etc. up-to 500).


### Example Usage in the Application

1. **Login as Admin:**

   * **Username**: `admin`
   * **Password**: `admin123`

2. **Login as Provider:**

   * **Username**: `provider1`
   * **Password**: `password123`

3. **Login as Attendant:**

   * **Username**: `attendant1`
   * **Password**: `password123`

4. **Login as Driver:**

   * **Username**: `driver1`
   * **Password**: `password123`

### Additional Information

* **Admin Role**: Full control over the application.
* **Provider Role**: Manage parking facilities, spot availability, and revenue.
* **Attendant Role**: Oversee daily operations of parking facilities.
* **Driver Role**: Users who book parking spots at different facilities.

> **Note**: All users are seeded with the password `password123`. You may change the passwords via the admin panel after logging in.


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

Create **`frontend/src/services/api.ts`**

```javascript
import axios from "axios";
import Cookies from "js-cookie";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api/",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = Cookies.get("access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### 2. Example Auth API

**`frontend/src/api/services/authServices.ts`**

```javascript
import api from "./api.ts";
import Cookies from "js-cookie";

import api from "./api";
import Cookies from "js-cookie";

// Login user and store tokens in cookies
export const login = async (username: string, password: string) => {
  const response = await api.post("api/accounts/login/", { username, password });

  if (response.data.access) {
    Cookies.set("access", response.data.access, { secure: true, sameSite: "Strict" });
    Cookies.set("refresh", response.data.refresh, { secure: true, sameSite: "Strict" });
  }

  return response.data;
};

// Logout user and clear cookies
export const logout = () => {
  await api.post("api/accounts/logout/", { refresh: Cookies.get('refresh') })
  Cookies.remove("access");
  Cookies.remove("refresh");
};

```

### 3. Fetch Example (Nearby Spots)

```javascript
import api from "./api";

// Fetch nearby parking spots based on user's location
export const getNearbySpots = async (lat: number, lng: number, radius = 2) => {
  const res = await api.get("api/parking/nearby/", {
    params: { lat, lng, radius },
  });
  return res.data;
};

```

### 4. Usage in a React Component

```jsx
import React, { useEffect, useState } from "react";
import { getNearbySpots } from "../api/services/parkingServices";

interface Spot {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
}

export default function NearbySpots() {
  const [spots, setSpots] = useState<Spot[]>([]);

  useEffect(() => {
    navigator.geolocation.getCurrentPosition((pos) => {
      getNearbySpots(pos.coords.latitude, pos.coords.longitude)
        .then((data) => setSpots(data))
        .catch((err) => console.error("Failed to fetch spots:", err));
    });
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Nearby Spots</h2>
      <ul className="space-y-2">
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
    "default": env.db(
        "DATABASE_URL", 
        default="postgres://username:password@localhost:5432/advanceparkingsystem"
    )
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

You can then use these keys in your `.env` files for both backend and frontend.

# Docker Setup for AdvanceParkingSystem

Project structure (with Docker):

```
advanceparkingsystem/
│── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── .env
│── docker-compose.yml
```

## `backend/Dockerfile`

```dockerfile
# Backend: Django + Gunicorn
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run migrations & collectstatic
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn core.wsgi:application --bind 0.0.0.0:8000"]
```



## `frontend/Dockerfile`

```dockerfile
# Frontend: React Vite
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy frontend code
COPY . .

# Build app
RUN npm run build

# Serve with a lightweight server
RUN npm install -g serve
CMD ["serve", "-s", "dist", "-l", "5173"]
```


## `docker-compose.yml`

```yaml
version: "3.9"

services:
  backend:
    build: ./backend
    container_name: aps-backend
    env_file: ./backend/.env
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build: ./frontend
    container_name: aps-frontend
    env_file: ./frontend/.env
    volumes:
      - ./frontend:/app
    ports:
      - "5173:5173"
    depends_on:
      - backend

  db:
    image: postgres:15
    container_name: aps-db
    restart: always
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```



## Running the System

1. **Build & start**

```bash
docker-compose up --build
```

2. **Apply migrations manually if first run**

```bash
docker exec -it aps-backend python manage.py migrate
```

3. **Access**

* Backend API → [http://localhost:8000/api](http://localhost:8000/api)
* Frontend → [http://localhost:5173](http://localhost:5173)
* Database → `localhost:5432`


## Pending Features

* [ ] Dynamic pricing engine.
* [ ] Background push notification delivery (Celery).
* [ ] WebSocket-based in-app notifications.
* [ ] Export reports (CSV/Excel).
* [ ] Admin dashboards for analytics.
* [ ] Dockerized AI training pipeline.

## License

MIT License – free to use, modify, and distribute.
