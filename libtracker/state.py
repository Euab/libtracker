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
    def __init__(self):
        self._states = {}

    def get(self, entity_id):
        return self._states.get(entity_id)

    def all(self):
        return [
            self._states[state].to_dict() for state in self._states
        ]

    def set(self, entity_id, new_state, attrs):
        entity_id = entity_id.lower()
        attrs = attrs or {}

        state = State(
            entity_id,
            new_state,
            attrs
        )

        self._states[entity_id] = state
