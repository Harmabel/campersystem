class UiService:

    def __init__(self, app):
        self.app = app

    async def forward_to_ui(self,data):
        message = {
            "type": "entity_update",
            "data": data
        }

        for ws in set(self.app["websockets"]):
            print('msg ui',message)
            await ws.send_json(message)