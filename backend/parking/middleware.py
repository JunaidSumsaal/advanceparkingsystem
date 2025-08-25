from django.utils.deprecation import MiddlewareMixin
from .models import SpotPredictionLog

class PredictionLoggingMiddleware(MiddlewareMixin):
    """
    Collect predicted results attached to the request (request.prediction_logs)
    and persist them once per response.
    """
    def process_response(self, request, response):
        logs = getattr(request, "prediction_logs", None)
        if isinstance(logs, list):
            for log in logs:
                SpotPredictionLog.objects.create(
                    parking_spot=log["spot"],
                    probability=log["probability"],
                    predicted_for_time=log["predicted_for_time"],
                    model_version=log.get("model_version", "v1"),
                )
        return response
