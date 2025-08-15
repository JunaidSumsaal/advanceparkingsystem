from prometheus_client import Counter, Histogram, Gauge

WS_CONNECTIONS = Counter('ws_connections_total', 'WebSocket connections established')
WS_MESSAGES_SENT = Counter('ws_messages_sent_total', 'WebSocket messages sent')
WS_SEND_LATENCY = Histogram('ws_send_latency_seconds', 'Latency of sending WS message')
WS_DISCONNECTS = Counter('ws_disconnects_total', 'WebSocket connections closed')
PREDICTION_REQUESTS = Counter('prediction_requests_total', 'Total prediction API requests')
PREDICTION_LATENCY = Histogram('prediction_latency_seconds', 'Prediction request latency')
PREDICTION_SAVED = Counter('prediction_saved_total', 'SpotPredictionLog rows saved')
BOOKING_CREATED = Counter('booking_created_total', 'Total bookings created')
BOOKING_ENDED = Counter('booking_ended_total', 'Total bookings ended')
ACTIVE_AVAILABLE_SPOTS = Counter('active_available_spots_total', 'Total active available spots')
SPOT_SELECTED = Counter('spot_selected_total', 'Total spots selected')
MODEL_TRAINING_REQUESTS = Counter(
    "spot_model_training_requests_total", "Number of model training runs"
)

MODEL_ACCURACY = Gauge(
    "spot_model_accuracy", "Latest model training accuracy"
)
