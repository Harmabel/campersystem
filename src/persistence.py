class Persistence:
    def __init__(self, db):
        self.db = db

    def load_definitions(self):
        rows = self.db.fetchall(
            "SELECT * FROM entiteiten"
        )
        return {
            row["id"]: dict(row)
            for row in rows
        }

    def load_states(self):
        rows = self.db.fetchall(
            "SELECT * FROM entity_states"
        )
        return {
            row["entity_id"]: {
                "state": row["state"],
                "value": row["value"],
                "ts": row["ts"]
            }
            for row in rows
        }

    def save_state(self, entityId, values):
        self.db.execute("""
            INSERT INTO entity_states (entity_id, state, value, ts)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                state = VALUES(state),
                value = VALUES(value),
                ts = VALUES(ts)
        """, (entityId, values.get("state"), values.get("value"), values.get("ts")))

    def save_definition(self, entityId, key, value):
        sql = f"UPDATE entiteiten SET `{key}` = %s WHERE id = %s"
        self.db.execute(sql, (value, entityId))

    def new_entity(self, sensorkey):
        return self.db.execute(
            "INSERT INTO entiteiten (sensorkey, active) VALUES (%s, 'N')",
            (sensorkey,)
        )
    def save_minmax(self, entityId, mm):
        self.db.execute("""
            INSERT INTO entity_minmax (entity_id, datum, min, max)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                min = VALUES(min),
                max = VALUES(max)
        """, (entityId, mm["datum"], mm["min"], mm["max"]))

    def load_minmax_today(self):
        rows = self.db.fetchall(
            "SELECT * FROM entity_minmax WHERE datum = CURDATE()"
        )
        return {
            row["entity_id"]: {
                "datum": row["datum"],
                "min": row["min"],
                "max": row["max"],
                "dirty": False
            }
            for row in rows
        }