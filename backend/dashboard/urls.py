from django.urls import path
from .views import AttendantDashboardView, DriverDashboardView, ProviderDashboardView, SpotEvaluationReportView

urlpatterns = [
  path("driver/", DriverDashboardView.as_view(), name="driver-dashboard"),
    path("attendant/", AttendantDashboardView.as_view(), name="attendant-dashboard"),
    path("provider/", ProviderDashboardView.as_view(), name="provider-dashboard"),
    path("spot-evaluations/", SpotEvaluationReportView.as_view(), name="spot-evaluations"),
]
