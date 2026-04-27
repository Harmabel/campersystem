from datetime import date

class EntityService:
    def __init__(self, entity_manager, bus, datetime):
        self.entity_manager = entity_manager
        self.bus = bus
        self.datetime = datetime

    async def handle_state(self, data):
        entityId = data["entityId"]
        state = data["value"]
        value = float(state) if data["veldtype"] == "number" else None

        entity = self.entity_manager.get_entity(entityId)
        if not entity:
            return

        # state opslaan
        await self.entity_manager.update_entity_values(
            entityId,
            state=state,
            value=value,
            ts=self.datetime.now(),
        )

        # min/max alleen bijwerken als het een getal is
        if value is not None:
            minmax_enabled = self.entity_manager.get_key_value(entityId, "minmax")
            if minmax_enabled == "J":
                self.entity_manager.update_minmax(entityId, value)

        ui_name = self.entity_manager.get_key_value(entityId, "ui_name")
        if not ui_name:
            return

        # await self.bus.emit("entity_updated", {
        #     "entityId": entityId,
        #     "updates": {
        #         "entityId": entityId,
        #         "state": state,
        #         "value": value
        #     }
        # })

        await self.bus.emit("entity_updated", {
            "type": "entity_update",
            "entityId": entityId,
            "ui_name": ui_name,
            "state": state,
            "value": value,
            "min": minmax.get("min"),
            "max": minmax.get("max")
        })