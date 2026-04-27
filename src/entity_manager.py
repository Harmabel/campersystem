from datetime import datetime, date

class Entity:
    def __init__(self, entityId, definition):
        self.entityId = entityId
        self.definition = definition      # vaste config uit entiteiten
        self.values = {                   # actuele state uit entity_states
            "state": None,
            "value": None,
            "ts": None
        }
        self.dirty = False

    def update_definition(self, key, value):
        self.definition[key] = value
        self.dirty = True

    def update_values(self, **updates):
        changed = False
        for key, value in updates.items():
            if value is None:
                continue
            if self.values.get(key) != value:
                self.values[key] = value
                changed = True
        if changed:
            self.values["ts"] = datetime.now()
            self.dirty = True
        return changed


class EntityManager:
    def __init__(self, persistence):
        self.persistence = persistence
        self.entities = {}       # entityId -> Entity
        self.sensor_index = {}   # sensorkey -> entityId
        self.dirty_entities = set()
        self.minmax = {}  # entityId -> {datum, min, max, dirty}

    def load_all(self):
        # laden definities
        definitions = self.persistence.load_definitions()
        for entityId, definition in definitions.items():
            sensorkey = definition["sensorkey"]
            entity = Entity(entityId, definition)
            self.entities[entityId] = entity
            if definition['active'] == 'J':
                self.sensor_index[sensorkey] = entityId
            else:
                self.sensor_index[sensorkey] = None

        # laden actuele states
        states = self.persistence.load_states()
        for entityId, state in states.items():
            if entityId in self.entities:
                self.entities[entityId].values = state

        # laden minmax van vandaag
        minmax_today = self.persistence.load_minmax_today()
        for entityId, mm in minmax_today.items():
            self.minmax[entityId] = mm

    def flush_to_db(self):
        if not self.dirty_entities:
            return
        for entityId in list(self.dirty_entities):
            entity = self.entities.get(entityId)
            if entity and entity.dirty:
                self.persistence.save_state(entityId, entity.values)
                entity.dirty = False
        for entityId, mm in self.minmax.items():
            if mm.get("dirty"):
                self.persistence.save_minmax(entityId, mm)
                mm["dirty"] = False

        self.dirty_entities.clear()

    def get_entity(self, entityId):
        return self.entities.get(entityId)

    def get_key_value(self, entityId, key):
        return self.entities[entityId].definition[key]

    def get_sensorkey(self, entityId, key=None):
        return self.entities[entityId].definition['sensorkey']

    def get_sensor_values(self, entityId):
        if entityId is None:
            return None
        return self.entities[entityId].values

    async def update_entity_values(self, entityId, **updates):
        entity = self.get_entity(entityId)
        if entity is None:
            return
        changed = entity.update_values(**updates)
        if changed:
            self.dirty_entities.add(entityId)

    def definition_update(self, entityId, key, value):
        self.entities[entityId].update_definition(key, value)
        self.persistence.save_definition(entityId, key, value)
        sensorkey = self.get_sensorkey(entityId)
        if key == 'active':
            if value == 'J':
                self.sensor_index[sensorkey] = entityId
            else:
                self.sensor_index[sensorkey] = None

    def convert_sensorkey(self, sensorkey):
        if sensorkey in self.sensor_index:
            return self.sensor_index.get(sensorkey)
        # nieuwe onbekende sensor — toevoegen als inactief
        entityId = self.persistence.new_entity(sensorkey)
        self.sensor_index[sensorkey] = None
        return None
    
    def update_minmax(self, entityId, value):
        today = date.today()
        minmax = self.minmax.get(entityId)

        if minmax is None or minmax["datum"] != today:
            # nieuwe dag of nog niet bekend — initialiseren
            self.minmax[entityId] = {"datum": today, "min": value, "max": value, "dirty": True}
        else:
            changed = False
            if value < minmax["min"]:
                minmax["min"] = value
                changed = True
            if value > minmax["max"]:
                minmax["max"] = value
                changed = True
            if changed:
                minmax["dirty"] = True