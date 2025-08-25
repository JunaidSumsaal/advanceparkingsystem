import json
import logging
import time
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class ParkingConsumer(AsyncWebsocketConsumer):
    GROUP = "parking_updates"

    async def connect(self):
        user = self.scope.get("user")
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()
        logger.info("WS connect channel=%s user=%s", self.channel_name, getattr(user, "username", None))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)
        logger.info("WS disconnect channel=%s code=%s", self.channel_name, close_code)

    async def receive(self, text_data):
        # no inbound commands for now
        return

    async def parking_update(self, event):
        payload = event.get("data", {})
        t0 = time.time()
        ok = True
        try:
            await self.send(text_data=json.dumps(payload))
        except Exception:
            ok = False
            logger.exception("WS parking_update send failed")
        logger.info("WS send latency=%.3fs ok=%s channel=%s", time.time() - t0, ok, self.channel_name)
