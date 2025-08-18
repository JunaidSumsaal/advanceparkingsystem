# core/admin.py
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.db.models import Avg, Count
from django.db.models.functions import TruncDay
from parking.models import ParkingSpot, Booking, SpotPredictionLog
import json

class MetricsAdmin(admin.ModelAdmin):
    change_list_template = "admin/metrics_dashboard.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("metrics/", self.admin_site.admin_view(self.metrics_view))
        ]
        return custom_urls + urls

    def metrics_view(self, request):
        # --- System metrics
        total_spots = ParkingSpot.objects.count()
        available_spots = ParkingSpot.objects.filter(is_available=True).count()
        active_bookings = Booking.objects.filter(is_active=True).count()

        # --- AI metrics
        total_preds = SpotPredictionLog.objects.count()
        avg_conf = SpotPredictionLog.objects.aggregate(avg_conf=Avg("probability"))["avg_conf"] or 0
        preds_per_spot = SpotPredictionLog.objects.values("parking_spot").annotate(count=Count("id")).count()

        # --- Trends: bookings per day (last 7 days)
        booking_trend = (
            Booking.objects.annotate(day=TruncDay("start_time"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        booking_labels = [b["day"].strftime("%Y-%m-%d") for b in booking_trend]
        booking_values = [b["count"] for b in booking_trend]

        # --- Trends: prediction logs per day (last 7 days)
        pred_trend = (
            SpotPredictionLog.objects.annotate(day=TruncDay("created_at"))
            .values("day")
            .annotate(count=Count("id"), avg_conf=Avg("probability"))
            .order_by("day")
        )
        pred_labels = [p["day"].strftime("%Y-%m-%d") for p in pred_trend]
        pred_counts = [p["count"] for p in pred_trend]
        pred_conf = [round(p["avg_conf"] or 0, 2) for p in pred_trend]

        # --- Render HTML
        html = f"""
        <h1>🚗 Parking System Metrics</h1>
        <h2>System</h2>
        <ul>
            <li>Total Spots: {total_spots}</li>
            <li>Available Spots: {available_spots}</li>
            <li>Active Bookings: {active_bookings}</li>
        </ul>

        <h2>🤖 AI Predictions</h2>
        <ul>
            <li>Total Predictions Logged: {total_preds}</li>
            <li>Average Confidence: {avg_conf:.2f}</li>
            <li>Spots with Predictions: {preds_per_spot}</li>
        </ul>

        <h2>📊 Trends</h2>
        <canvas id="bookingChart" width="400" height="200"></canvas>
        <canvas id="predictionChart" width="400" height="200"></canvas>

        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
        const bookingCtx = document.getElementById('bookingChart').getContext('2d');
        new Chart(bookingCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(booking_labels)},
                datasets: [{{
                    label: 'Bookings per Day',
                    data: {json.dumps(booking_values)},
                    borderColor: 'blue',
                    fill: false
                }}]
            }}
        }});

        const predCtx = document.getElementById('predictionChart').getContext('2d');
        new Chart(predCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(pred_labels)},
                datasets: [
                    {{
                        label: 'Predictions per Day',
                        data: {json.dumps(pred_counts)},
                        borderColor: 'green',
                        fill: false
                    }},
                    {{
                        label: 'Avg Confidence',
                        data: {json.dumps(pred_conf)},
                        borderColor: 'orange',
                        fill: false,
                        yAxisID: 'y1'
                    }}
                ]
            }},
            options: {{
                scales: {{
                    y: {{ beginAtZero: true }},
                    y1: {{
                        beginAtZero: true,
                        position: 'right'
                    }}
                }}
            }}
        }});
        </script>
        """
        return HttpResponse(html)

admin.site.register_view("metrics", view=MetricsAdmin.metrics_view, name="System Metrics")
