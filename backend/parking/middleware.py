from parking.models import SpotPredictionLog
from django.utils.deprecation import MiddlewareMixin

class PredictionLoggingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if hasattr(request, "prediction_logs") and isinstance(request.prediction_logs, list):
            for log in request.prediction_logs:
                SpotPredictionLog.objects.create(
                    parking_spot=log["spot"],
                    probability=log["probability"],
                    predicted_for_time=log["predicted_for_time"],
                    model_version="v1"
                )
        return response
