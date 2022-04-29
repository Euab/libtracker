from abc import ABC
from collections import defaultdict


class Entity(ABC):
    @property
    def name(self):
        return "Generic Entity"

    @property
    def state(self):
        return "Unknown"

    @property
    def state_attrs(self):
        return {}

    def update(self):
        pass

    sm = None
    entity_id = None

    def push_state(self):
        if self.sm is None:
            raise AttributeError("StateMachine attribute is none.")
        if self.entity_id is None:
            raise AttributeError("Entity ID needs to be defined.")

        state = str(self.state)
        attrs = self.state_attrs or {}

        attrs.update(defaultdict(dict).get(self.entity_id, {}))
        self.sm.set(self.entity_id, state, attrs)
