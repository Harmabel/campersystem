import asyncio
import aiohttp_cors
from aiohttp import web
from datetime import datetime

from entity_manager import EntityManager
from persistence import Persistence
from entity_service import EntityService
from entity_saver import EntitySaver
from entity_api import patch_entity
from ui_service import UiService
from init_db import init_db
from bus import EventBus
from state import StateStore
from init_mqtt import init_mqtt
from ws_handler import ws_handler
from relais import RelaisMonitor

def main():

    monitor = RelaisMonitor(pin=23, callback=status_gewijzigd)
        
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=8080)



def status_gewijzigd(aan):
    print(f"Relais: {'AAN' if aan else 'UIT'}")
    # hier kun je ook een MQTT bericht publiceren



def create_app():

    bus = EventBus()
    state = StateStore()
    db = init_db()
    persistence = Persistence(db)

    entity_manager = EntityManager(persistence)
    entity_manager.load_all()


    entity_service = EntityService(
        entity_manager, bus, datetime
    )

    bus.on("state_received", entity_service.handle_state)

    app = web.Application()

    # store dependencies
    app["bus"] = bus
    app["state"] = state
    app["db"] = db
    app["persistence"] = persistence
    app["entity_manager"] = entity_manager
    app["entity_service"] = entity_service

    # websocket
    app["websockets"] = set()
    app.router.add_get("/ws", ws_handler)

    ui_service = UiService(app)
    bus.on("entity_updated", ui_service.forward_to_ui)

    # api
    app.router.add_patch("/api/entities/{id}", patch_entity)

    # cors
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods=["GET", "POST", "PATCH", "OPTIONS"]
        )
    })

    for route in list(app.router.routes()):
        cors.add(route)

    # lifecycle hooks
    app.on_startup.append(start_background_services)
    app.on_cleanup.append(stop_background_services)

    return app

async def start_background_services(app):
    print("STARTUP CALLED")
    bus = app["bus"]
    state = app["state"]
    db = app["db"]
    entity_manager = app["entity_manager"]
    persistence = app["persistence"]

    # MQTT
    mqtt = init_mqtt(bus=bus, state=state, db=db)
    app["mqtt"] = mqtt
    await mqtt.start(entity_manager)

    # Entity saver
    saver = EntitySaver(entity_manager, persistence)
    app["entity_saver"] = saver
    app["saver_task"] = asyncio.create_task(saver.run())

    print("Background services gestart")

async def stop_background_services(app):

    app["entity_saver"].running = False
    app["saver_task"].cancel()

    await app["mqtt"].stop()

    print("Background services gestopt")

if __name__ == "__main__":
    main()