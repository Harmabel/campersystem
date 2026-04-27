# mqtt_listener.py

import paho.mqtt.client as MQTTClient
import json
import asyncio

class MQTTListener():
    def __init__(self, bus, host):
        self.bus = bus
        # self.state = state
        self.host = host
        self.client = MQTTClient("campersystem")

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    async def start(self, entity_manager):
        self.entity_manager = entity_manager
        await self.client.connect(self.host,self.port)

    async def stop(self):
        print("MQTT stopping")
        await self.client.disconnect()

    def on_connect(self, client, flags, rc, properties):
        print("✅ MQTT connected")
        client.subscribe("Rutx50")
        client.subscribe("zigbee2mqtt")

    async def on_message(self, client, topic, payload, qos, properties):
        device_id, msgdata = await self.msg_parse(payload,topic)
 
        for sensorkey, value in msgdata:
            entityId = self.entity_manager.convert_sensorkey(str(sensorkey))
            if entityId is not None:
                value = str(value)
                await self.bus.emit("state_received", {
                    "entityId": entityId,
                    "value": value
                })

    async def run(self):
        await self.connect()
        # task levend houden
        await asyncio.Event().wait()

    def msg_parse(self,payload,topic):
        raw = payload.decode("utf-8")
        if raw == 'Online':
            return
        if raw == 'Offline':
            return
        if raw == 'OFF':
            return
        if raw == 'ON':
            return
        if raw.startswith("b'") or raw.startswith('b"'):
            raw = raw[2:-1]   # verwijder b' en '
        data = json.loads(raw)
        topic_parts = topic.split('/')
        print('topic_parts'),topic_parts