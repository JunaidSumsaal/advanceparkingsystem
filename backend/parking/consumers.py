import json
import logging
import time
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class ParkingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        await self.channel_layer.group_add("parking_updates", self.channel_name)
        await self.accept()
        
        logger.info(f"WS connect: channel={self.channel_name} user={getattr(user,'username',None)}")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("parking_updates", self.channel_name)
        logger.info(f"WS disconnect: channel={self.channel_name} code={close_code}")

    async def receive(self, text_data):
        # Not expecting incoming messages for now
        pass

    async def parking_update(self, event):
        data = event.get("data", {})
        send_start = time.time()
        try:
            await self.send(text_data=json.dumps(event["data"]))
            success = True
        except Exception as e:
            logger.exception("Failed to send WS parking_update")
            success = False
        latency = time.time() - send_start
        # SRE: log delivery latency & success
        logger.info(f"WS send latency={latency:.3f}s success={success} channel={self.channel_name}")

