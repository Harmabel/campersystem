import aiohttp  
from aiohttp import web

async def ws_handler(request):
    print('ws handler')
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    # registreer de nieuwe verbinding
    request.app["websockets"].add(ws)
    
    # stuur meteen alle huidige entities naar deze client
    entity_manager = request.app["entity_manager"]
    for entityId, entity in entity_manager.entities.items():
        if entity.definition.get("ui_name"):
            minmax = entity_manager.minmax.get(entityId, {})
            values = entity.values
            message = {
                "type": "entity_update",
                "entityId": entityId,
                "ui_name": entity.definition.get("ui_name"),
                "state": values.get("state"),
                "value": values.get("value"),
                "min": minmax.get("min"),
                "max": minmax.get("max")
            }
            print('ws.send',message)
            await ws.send_json(message)
    
    # daarna gewoon de normale message loop
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            pass  # inkomende berichten verwerken indien nodig
        elif msg.type == aiohttp.WSMsgType.ERROR:
            break
    
    request.app["websockets"].discard(ws)
    return ws

