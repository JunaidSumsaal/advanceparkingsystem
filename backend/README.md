# Backend API Routes Documentation

This document provides an overview of the API routes available in the backend, organized by functional areas. Each route includes the HTTP method, path, view, and a brief description.

## Accounts

| Route                                                          | View                                                 | Description                                      |
| -------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------ |
| `/api/accounts/`                                               | `rest_framework.routers.APIRootView`                 | API root for accounts                            |
| `/api/accounts/<drf_format_suffix:format>`                     | `rest_framework.routers.APIRootView`                 | API root with format suffix                      |
| `/api/accounts/register/`                                      | `accounts.views.RegisterView`                        | Register a new user                              |
| `/api/accounts/login/`                                         | `rest_framework_simplejwt.views.TokenObtainPairView` | Obtain JWT token pair (login)                    |
| `/api/accounts/logout/`                                        | `accounts.views.LogoutView`                          | Logout current user                              |
| `/api/accounts/refresh/`                                       | `rest_framework_simplejwt.views.TokenRefreshView`    | Refresh JWT token                                |
| `/api/accounts/change-password/`                               | `accounts.views.ChangePasswordView`                  | Change user password                             |
| `/api/accounts/profile/`                                       | `accounts.views.ProfileView`                         | Retrieve or update user profile                  |
| `/api/accounts/admin/users/`                                   | `accounts.views.AdminUserViewSet`                    | List all users (admin)                           |
| `/api/accounts/admin/users/<pk>/`                              | `accounts.views.AdminUserViewSet`                    | Retrieve, update, delete a specific user (admin) |
| `/api/accounts/admin/users/add-attendant/`                     | `accounts.views.AddAttendantView`                    | Add a new attendant (admin)                      |
| `/api/accounts/admin/facilities/<int:facility_id>/attendants/` | `accounts.views.FacilityAttendantManageView`         | Manage attendants for a facility (admin)         |
| `/api/accounts/logs/`                                          | `accounts.views.AuditLogListView`                    | List audit logs                                  |
| `/api/accounts/logs/export/`                                   | `accounts.views.AuditLogExportView`                  | Export audit logs                                |
| `/api/accounts/newsletter/`                                    | `accounts.views.NewsletterSubscriptionView`          | Manage newsletter subscription                   |
| `/api/accounts/newsletter/subscribe/`                          | `accounts.views.PublicNewsletterSubscriptionView`    | Public newsletter subscription                   |


## Dashboard

| Route                             | View                                       | Description              |
| --------------------------------- | ------------------------------------------ | ------------------------ |
| `/api/dashboardattendant/`        | `dashboard.views.AttendantDashboardView`   | Dashboard for attendants |
| `/api/dashboarddriver/`           | `dashboard.views.DriverDashboardView`      | Dashboard for drivers    |
| `/api/dashboardprovider/`         | `dashboard.views.ProviderDashboardView`    | Dashboard for providers  |
| `/api/dashboardspot-evaluations/` | `dashboard.views.SpotEvaluationReportView` | Spot evaluation reports  |


## Metrics

| Route           | View                                           | Description         |
| --------------- | ---------------------------------------------- | ------------------- |
| `/api/metrics/` | `core.views.metrics_view`                      | Application metrics |
| `/metrics`      | `django_prometheus.exports.ExportToDjangoView` | Prometheus metrics  |


## Notifications

| Route                                  | View                                              | Description                             |
| -------------------------------------- | ------------------------------------------------- | --------------------------------------- |
| `/api/notifications/email-preference/` | `notifications.views.EmailPreferenceUpdateView`   | Update email notification preferences   |
| `/api/notifications/history/`          | `notifications.views.NotificationHistoryView`     | View notification history               |
| `/api/notifications/notifications/`    | `notifications.views.NotificationListView`        | List notifications                      |
| `/api/notifications/subscribe/`        | `notifications.views.PushSubscriptionCreateView`  | Subscribe to push notifications         |
| `/api/notifications/subscriptions/`    | `notifications.views.PushSubscriptionListView`    | List push subscriptions                 |
| `/api/notifications/unsubscribe/`      | `notifications.views.UnsubscribeNotificationView` | Unsubscribe from notifications          |
| `/notifications/`                      | `notifications.views.NotificationViewSet`         | List notifications (alternate endpoint) |
| `/notifications/<pk>/read/`            | `notifications.views.NotificationViewSet`         | Mark a notification as read             |
| `/notifications/mark_all_read/`        | `notifications.views.NotificationViewSet`         | Mark all notifications as read          |
| `/notifications/unread_count/`         | `notifications.views.NotificationViewSet`         | Get count of unread notifications       |
| `/push-subscriptions/`                 | `notifications.views.PushSubscriptionViewSet`     | List push subscriptions                 |
| `/push-subscriptions/<pk>/`            | `notifications.views.PushSubscriptionViewSet`     | Retrieve a push subscription            |


## Parking

| Route                                     | View                                        | Description                         |
| ----------------------------------------- | ------------------------------------------- | ----------------------------------- |
| `/api/parking/`                           | `rest_framework.routers.APIRootView`        | Parking API root                    |
| `/api/parking/availability/logs/`         | `parking.views.SpotAvailabilityLogListView` | List spot availability logs         |
| `/api/parking/book/`                      | `parking.views.BookParkingSpotView`         | Book a parking spot                 |
| `/api/parking/bookings/`                  | `parking.views.BookingViewSet`              | List bookings                       |
| `/api/parking/bookings/<pk>/`             | `parking.views.BookingViewSet`              | Booking detail                      |
| `/api/parking/bookings/<pk>/end_booking/` | `parking.views.BookingViewSet`              | End a booking                       |
| `/api/parking/facilities/`                | `parking.views.ParkingFacilityView`         | List parking facilities             |
| `/api/parking/facilities/<pk>/`           | `parking.views.ParkingFacilityView`         | Facility detail                     |
| `/api/parking/facilities/<pk>/archive/`   | `parking.views.ParkingFacilityView`         | Archive facility                    |
| `/api/parking/facilities/<pk>/restore/`   | `parking.views.ParkingFacilityView`         | Restore archived facility           |
| `/api/parking/navigate/<int:spot_id>/`    | `parking.views.NavigateToSpotView`          | Navigate to a specific parking spot |
| `/api/parking/nearby/`                    | `parking.views.NearbyParkingSpotsView`      | List nearby parking spots           |
| `/api/parking/predictions/nearby/`        | `parking.views.NearbyPredictionsView`       | Predict nearby spot availability    |
| `/api/parking/pricing/logs/`              | `parking.views.SpotPriceLogView`            | Spot pricing logs                   |
| `/api/parking/pricing/update/`            | `parking.views.trigger_dynamic_pricing`     | Trigger dynamic pricing update      |
| `/api/parking/review/`                    | `parking.views.SpotReviewCreateView`        | Create a review for a spot          |
| `/api/parking/spots/`                     | `parking.views.ParkingSpotViewSet`          | List parking spots                  |
| `/api/parking/spots/<pk>/`                | `parking.views.ParkingSpotViewSet`          | Parking spot detail                 |
| `/api/parking/spots/<pk>/archive/`        | `parking.views.ParkingSpotViewSet`          | Archive spot                        |
| `/api/parking/spots/<pk>/restore/`        | `parking.views.ParkingSpotViewSet`          | Restore archived spot               |


## Admin Portal

| Route                                             | View                                           | Description                  |
| ------------------------------------------------- | ---------------------------------------------- | ---------------------------- |
| `/portal/admin/`                                  | `django.contrib.admin.sites.index`             | Admin dashboard              |
| `/portal/admin/<app_label>/`                      | `django.contrib.admin.sites.app_index`         | App-specific admin dashboard |
| `/portal/admin/accounts/user/`                    | `django.contrib.admin.options.changelist_view` | Manage users in admin        |
| `/portal/admin/accounts/auditlog/`                | `django.contrib.admin.options.changelist_view` | Manage audit logs in admin   |
| `/portal/admin/parking/booking/`                  | `django.contrib.admin.options.changelist_view` | Manage bookings in admin     |
| `/portal/admin/parking/parkingfacility/`          | `django.contrib.admin.options.changelist_view` | Manage facilities in admin   |
| `/portal/admin/parking/parkingspot/`              | `django.contrib.admin.options.changelist_view` | Manage spots in admin        |
| `/portal/admin/token_blacklist/blacklistedtoken/` | `django.contrib.admin.options.changelist_view` | Manage blacklisted tokens    |
| `/portal/admin/token_blacklist/outstandingtoken/` | `django.contrib.admin.options.changelist_view` | Manage outstanding tokens    |

