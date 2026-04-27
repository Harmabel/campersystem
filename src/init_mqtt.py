# mqtt/init.py
from mqtt_device import MQTTDevice

def init_mqtt(bus, state, db, host="localhost"):
    return MQTTDevice(bus, state, host, db)


