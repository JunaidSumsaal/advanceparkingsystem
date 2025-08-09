from prometheus_client import Counter, Histogram

WS_CONNECTIONS = Counter('ws_connections_total', 'WebSocket connections established')
WS_MESSAGES_SENT = Counter('ws_messages_sent_total', 'WebSocket messages sent')
WS_SEND_LATENCY = Histogram('ws_send_latency_seconds', 'Latency of sending WS message')
WS_DISCONNECTS = Counter('ws_disconnects_total', 'WebSocket connections closed')