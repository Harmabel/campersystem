class HistoryService:

    def __init__(self,datetime, entity_manager, persistence,bus):
        self.entity_manager = entity_manager
        self.bus = bus
        self.datetime = datetime
        self.persistence = persistence

    def minmax(self, entity_id, value, min_val, max_val, last_ts):
        minmax = self.entity_manager.get_key_value(entity_id, "minmax")

        if minmax != 'J':
            return None,None
        
        now = self.datetime.now()
        if not last_ts or last_ts.day != now.day:
            return value, value

        min_val = value if min_val is None else min(min_val, value)
        max_val = value if max_val is None else max(max_val, value)

        return min_val, max_val

    def history_update(self, entity_id, state, old_state, hist_ts):
        history = self.entity_manager.get_key_value(entity_id, "history")
        if history != 'J':
            return

        interval = self.entity_manager.get_key_value(entity_id, "hist_interval")

        # opslag bij verandering
        if interval == 99:
            if state != old_state:
                self.persistence.history_update(entity_id, state)
            return

        interval_sec = int(interval * 60)
        now = self.datetime.now()

        if not hist_ts or (now - hist_ts).seconds > interval_sec:
            self.persistence.history_update(entity_id, state)
            self.entity_manager.hist_ts_update(entity_id, now)
           
    def process_state(self, entity, state, value):
        if entity:
            values = entity.values

            min_val, max_val = self.minmax(
                entity.entityId,
                value,
                values.get("min"),
                values.get("max"),
                values.get("ts"),
            )

            self.history_update(
                entity.entityId,
                state,
                values.get("state"),
                values.get("hist_ts"),
            )

        return min_val, max_val