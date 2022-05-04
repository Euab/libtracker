from typing import Collection, Any, List


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
    def __init__(self, entity_id: str, state: str, attrs: dict) -> None:
        self.entity_id = entity_id.lower()
        self.state = state
        self.attrs = attrs or {}

    def to_dict(self) -> dict[str, Collection[Any]]:
        return {
            "entity_id": self.entity_id,
            "state": self.state,
            "attrs": self.attrs
        }


class StateMachine:
    """
    Class to hold states to track the state of different entities.
    """
    def __init__(self) -> None:
        self._states: dict = {}

    def get(self, entity_id: str) -> State:
        """
        Look up a specific state by entity id.
        :param entity_id: The unique ID of the state.
        :return: The corresponding state object.
        """
        return self._states.get(entity_id)

    def all(self) -> List[dict[str, Collection[Any]]]:
        """
        Get a list of dictionary representations of all states.
        :return: A list of all state dictionary representations.
        """
        return [
            self._states[state].to_dict() for state in self._states
        ]

    def set(self, entity_id: str, new_state: str, attrs: dict) -> None:
        """
        Set a new state inside the state machine.
        :param entity_id: The unique ID of the state.
        :param new_state: The new state to set the entity to.
        :param attrs: Any additional attributes to be stored within the state.
        :return: None
        """
        entity_id = entity_id.lower()
        attrs = attrs or {}

        state = State(
            entity_id,
            new_state,
            attrs
        )

        self._states[entity_id] = state
