class StateStore:
    def __init__(self):
        self._states = {}

    def set(self, entityId, value):
        old = self._states.get(entityId)
        if old == value:
            return none

        # er is dus een verandering, dan states bijwerken
        self._states[entityId] = value
        return {
            "entityId": entityId,
            "old": old,
            "new": value
        }


    def changes(self, updates: dict):
        changes = []

        for entityId, value in updates.items():
            old = self._states.get(entityId)
            if old != value:
                self._states[entityId] = value
                changes.append({
                    "entityId": entityId,
                    "old": old,
                    "new": value
                })

        return changes






    def get(self, entityId: str):
        return self._states.get(entityId)

    def all(self):
        return dict(self._states)