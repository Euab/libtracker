from abc import ABC
from collections import defaultdict

from libtracker.constants import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_SILENT
)

AREA_STATE = "zoning"  # Area is only in one state which is that it exists.


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
        return self.sm.set(self.entity_id, state, attrs)


class Zone(Entity):
    def __init__(self, sm, name, latitude, longitude, radius, silent):
        self.sm = sm
        self._name = name
        self._latitude = latitude
        self._longitude = longitude
        self._radius = radius
        self._silent = silent

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return AREA_STATE

    @property
    def state_attrs(self):
        attrs = {
            ATTR_LATITUDE: self._latitude,
            ATTR_LONGITUDE: self._longitude
        }

        if self._silent:
            attrs[ATTR_SILENT] = self._silent

        return attrs


class Trackable(Entity):
    pass
