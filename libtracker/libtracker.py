import json

from libtracker.constants import EVENT_STATE_CHANGED, ATTR_ENTITY_ID


class Bus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type in self._subscribers:
            self._subscribers[event_type].append(callback)
        else:
            self._subscribers[event_type] = [callback]

    def post(self, event_type, event_data=None):
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(event_data)


class State:
    """
    Representation of a state inside the state machine.

    State production rules:
        entity_id ::= <domain>.<object_id>
        domain ::= <string>
        object_id ::= <string>

    Where domain represents the type of object (i.e. device)
    and object_id represents the name of an object being represented by a
    state.
    """
    def __init__(self, entity_id, state, attrs):
        self.entity_id = entity_id.lower()
        self.state = state
        self.attrs = attrs or {}

    def to_dict(self):
        return {
            "entity_id": self.entity_id,
            "state": self.state,
            "attrs": self.attrs
        }


class StateMachine:
    def __init__(self, bus):
        self._states = {}
        self._bus = bus

    def get(self, entity_id):
        return self._states.get(entity_id)

    def set(self, entity_id, new_state, attrs):
        entity_id = entity_id.lower()
        attrs = attrs or {}

        state = State(
            entity_id,
            new_state,
            attrs
        )

        self._states[entity_id] = state
        self._bus.post(
            EVENT_STATE_CHANGED,
            {
                ATTR_ENTITY_ID: entity_id,
                "new_state": state
            }
        )
