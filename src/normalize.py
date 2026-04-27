import json

async def topic_parse(topic):
    # bepaald device_ id, als prefix voor entityId
    parts = topic.split('/')
    match parts[0]:
        case "ems-esp":
                device_id = 'wp'
        case "tele":
                device_id = 'son:'+ parts[2]
        case "stat": 
                device_id = 'son:'+ parts[2]

    return device_id

async def payload_parse(payload,device_id):
    # normalize payload naar dict
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
    print(data)
    return(data)

async def topic_parse(topic):
    # bepaald device_ id, als prefix voor entityId
    parts = topic.split('/')
    match parts[0]:
        case "ems-esp":
                device_id = 'wp'
        case "tele":
                device_id = 'son:'+ parts[2]
        case "stat": 
                device_id = 'son:'+ parts[2]

    return device_id

async def payload_parse(payload,device_id):
    # normalize payload naar dict
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
    return msgdata

async def detect_veldtype(raw_value: str) -> str:
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