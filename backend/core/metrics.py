from prometheus_client import Counter, Histogram

WS_CONNECTIONS = Counter('ws_connections_total', 'WebSocket connections established')
WS_MESSAGES_SENT = Counter('ws_messages_sent_total', 'WebSocket messages sent')
WS_SEND_LATENCY = Histogram('ws_send_latency_seconds', 'Latency of sending WS message')
WS_DISCONNECTS = Counter('ws_disconnects_total', 'WebSocket connections closed')
PREDICTION_REQUESTS = Counter('prediction_requests_total', 'Total prediction API requests')
PREDICTION_LATENCY = Histogram('prediction_latency_seconds', 'Prediction request latency')
PREDICTION_SAVED = Counter('prediction_saved_total', 'SpotPredictionLog rows saved')
