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

---

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

---

## Pending Features

* [ ] Dynamic pricing engine.
* [ ] Background push notification delivery (Celery).
* [ ] WebSocket-based in-app notifications.
* [ ] Export reports (CSV/Excel).
* [ ] Admin dashboards for analytics.
* [ ] Dockerized AI training pipeline.

## License

MIT License – free to use, modify, and distribute.
