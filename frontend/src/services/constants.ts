export const API =
  import.meta.env.MODE === "development"
    ? import.meta.env.VITE_API_URL || '/api'
    : "https://advancepackingsystem-backend.onrender.com/api";
;
export const SECURE = import.meta.env.VITE_API_SECURE || false;

// Core API prefixes
export const AUTH = `/accounts`;
export const ADMIN = `/admin`;
export const DASHBOARD = `/dashboard`;
export const PARKING = `/parking`;
export const NOTIFICATIONS = `/notifications`;
export const metrics = `/metrics`;

// Dashboard sub-routes
export const DASH_ADMIN = `/dashboard/admin`;
export const DASH_ADMIN_USERS = `/dashboard/admin/users`;
export const DASH_DRIVER = `/dashboard/driver`;
export const DASH_ATTENDANT = `/dashboard/attendant`;
export const DASH_PROVIDER = `/dashboard/provider`;
export const DASH_SPOT_EVAL = `/dashboard/spot-evaluations`;

// Parking sub-routes
export const PARK_AVAILABILITY_LOGS = `/availability/logs`;
export const PARK_BOOK = `/book`;
export const PARK_BOOKINGS = `/bookings`;
export const PARK_FACILITIES = `/facilities`;
export const PARK_SPOTS = `/spots`;
export const PARK_NEARBY = `/nearby`;
export const PARK_NAVIGATE = `/navigate`;
export const PARK_PREDICTIONS = `/predictions/nearby`;
export const PARK_PRICING_LOGS = `/pricing/logs`;
export const PARK_PRICING_UPDATE = `/pricing/update`;
export const PARK_REVIEW = `/review`;

// Notification sub-routes
export const NOTIF_LIST = `/notifications`;
export const NOTIF_HISTORY = `/history`;
export const NOTIF_EMAIL_PREF = `/email-preference`;
export const NOTIF_UNSUBSCRIBE = `/unsubscribe`;
export const NOTIF_PUSH = `/push-subscriptions`;

// Newsletter
export const NEWSLETTER = `/newsletter`;
export const NEWSLETTER_SUBSCRIBE = `/newsletter/subscribe`;

