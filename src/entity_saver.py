# entity_saver.py
import asyncio

class EntitySaver:
    def __init__(self, entity_manager, persistence, interval=30):
        self.entity_manager = entity_manager
        self.persistence = persistence
        self.interval = interval  # seconden
        self.running = True

    async def run(self):
        while self.running:
            await asyncio.sleep(self.interval)
            self.entity_manager.flush_to_db()