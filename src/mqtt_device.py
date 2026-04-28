from gmqtt import Client as MQTTClient

import json
# from normalize import topic_parse, payload_parse,detect_veldtype
import asyncio

class MQTTDevice:
    def __init__(self, bus, state, host, db):
        self.bus = bus
        self.state = state
        self.host = host
        self.db = db
        self.client = MQTTClient("campersystem")

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    async def start(self, entity_manager):
        self.entity_manager = entity_manager
        await self.client.connect(self.host)

    async def stop(self):
        print("MQTT stopping")
        await self.client.disconnect()

    def on_connect(self, client, flags, rc, properties):
        print("✅ MQTT connected")
        client.subscribe("zigbee2mqtt/Buitensensor")   
        client.subscribe("zigbee2mqtt/Binnensensor") 
        client.subscribe("zigbee2mqtt/Binnensensor_voor") 
        client.subscribe("zigbee2mqtt/Switch") 
        client.subscribe("zigbee2mqtt/Netspanning") 
    async def on_command(self, event):

        entityId = event["entityId"]
        action = event["action"]

        topic = entityId.replace(".", "/") + "/set"
        payload = action

        print(f"📤 MQTT {topic} = {payload}")
        self.client.publish(topic, payload)

    async def on_message(self, client, topic, payload, qos, properties):
        print(topic)
        sensorkey,msgdata = self.parse_msgdata(topic,payload)
        for sensorkey, value in msgdata:
            entityId = self.entity_manager.convert_sensorkey(str(sensorkey))
            if entityId is not None:
                veldtype = await self.detect_veldtype(str(value))
                value = str(value)
                await self.bus.emit("state_received", {
                    "entityId": entityId,
                    "value": value,
                    "veldtype": veldtype
                })
    async def run(self):
        await self.connect()
        # task levend houden
        await asyncio.Event().wait()
    
    def parse_msgdata(self,topic,payload):
        parts = topic.split('/')
        device_id = parts[0]
        if len(parts)> 1:
            match parts[0]:
                case "RUTX50":
                        device_id = parts[1]
                case "zigbee2mqtt":
                        device_id = parts[1]
                case "tele": 
                        device_id = parts[1]
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
        msgdata = []
        for key,value in data.items():
            if isinstance(value,dict) == True:
                for subkey, subvalue in value.items():
                    sensor_id = device_id+':'+key+":"+subkey
                    msgdata.append([sensor_id,subvalue])
            else:
                sensor_id = device_id+'-'+key
                msgdata.append([sensor_id,value])
        return device_id,msgdata

    async def detect_veldtype(self,raw_value: str) -> str:
        v = raw_value.strip().lower()

        # 1. boolean-achtig
        if v in ("on", "off", "true", "false", "0", "1"):
            return "bool"

        # 2. numeriek
        try:
            float(v)
            return "number"
        except ValueError:
            pass

        # 3. fallback
        return "text"