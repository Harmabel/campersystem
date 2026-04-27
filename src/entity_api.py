# api/entities.py
from aiohttp import web

async def patch_entity(request):
    entity_service = request.app["entity_service"]
 
    entityId = int(request.match_info["id"])
 
    data = await request.json()

    entity_service.set_configdata(data)

    return web.json_response({"status": "ok"})