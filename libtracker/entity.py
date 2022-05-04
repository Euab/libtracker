from abc import ABC
from collections import defaultdict
from typing import Any


class Entity(ABC):
    """
    Abstract base class to represent a entity inside the state machine.
    """
    @property
    def name(self) -> str:
        """ Get the name of the entity """
        return "Generic Entity"

    @property
    def state(self) -> str:
        """ Get the state of the entity """
        return "Unknown"

    @property
    def state_attrs(self) -> dict[str, Any]:
        """ Get attributes about this entity. """
        return {}

    def update(self) -> None:
        """ Update entity attributes """
        pass

    sm = None
    entity_id = None

    def push_state(self) -> None:
        if self.sm is None:
            raise AttributeError("StateMachine attribute is none.")
        if self.entity_id is None:
            raise AttributeError("Entity ID needs to be defined.")

        state = str(self.state)
        attrs = self.state_attrs or {}

        attrs.update(defaultdict(dict).get(self.entity_id, {}))
        self.sm.set(self.entity_id, state, attrs)
