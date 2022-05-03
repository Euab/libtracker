import math

from libtracker.entity import Entity
from libtracker.constants import ATTR_LATITUDE, ATTR_LONGITUDE, ATTR_RADIUS

ZONE_STATE = "zoning"

STATE_HOME = "home"
STATE_AWAY = "away"

DEFAULT_ZONE_RADIUS = 100  # m

VINCENTY_CONVERGENCE_THRESHOLD = 1e-12
VINCENTY_MAX_ITERATIONS = 200

EARTH_SEMI_MAJOR_AXIS = 6378137.0
EARTH_SEMI_MINOR_AXIS = 6356752.314245


def setup_home_zone(sm, config):
    h_zone = Zone(sm, config["home_name"], config[ATTR_LATITUDE],
                  config[ATTR_LONGITUDE], DEFAULT_ZONE_RADIUS)
    h_zone.entity_id = "zone.home"
    h_zone.push_state()


def in_zone(zone, latitude, longitude, radius=0):
    zone_distance = inverse_vincenty(
        (float(zone.attrs[ATTR_LATITUDE]), float(zone.attrs[ATTR_LONGITUDE])),
        (float(latitude), float(longitude))
    ) * 1000  # km -> m

    return zone_distance - radius < zone.attrs[ATTR_RADIUS]


def inverse_vincenty(theta_1, theta_2):
    """
    Inverse Vincenty formula to calculate the distance between two points on an
    assumed oblate spheroid.
    Where:
        ϕ1 = tuple(latitude, longitude)
        ϕ2 = tuple(latitude, longitude)
    Result is returned in kilometers.
    Reference:
    https://nathanrooy.github.io/posts/2016-12-18/vincenty-formula-with-python/
    """

    # If the two points are coincident
    if theta_1[0] == theta_2[0] and theta_1[1] == theta_2[1]:
        return 0.00

    flattening = 1 / 298.257223563  # f = (a - b) / a

    u1 = math.atan((1 - flattening) * math.tan(math.radians(theta_1[0])))
    u2 = math.atan((1 - flattening) * math.tan(math.radians(theta_2[0])))
    l = math.radians(theta_2[1] - theta_1[1])
    _lambda = l

    sin_u1 = math.sin(u1)
    cos_u1 = math.cos(u1)
    sin_u2 = math.sin(u2)
    cos_u2 = math.cos(u2)

    for i in range(VINCENTY_MAX_ITERATIONS):
        sin_lambda = math.sin(_lambda)
        cos_lambda = math.cos(_lambda)

        sin_sigma = math.sqrt((cos_u2 * sin_lambda) ** 2 +
                              (cos_u1 * sin_u2 - sin_u1 * cos_u2 * cos_lambda)
                              ** 2
                              )

        # Check again if the points are coincident
        if sin_sigma == 0:
            return 0.00

        cos_sigma = sin_u1 * sin_u2 + cos_u1 * cos_u2 * cos_lambda
        sigma = math.atan2(sin_sigma, cos_sigma)

        sin_alpha = cos_u1 * cos_u2 * sin_lambda / sin_sigma
        cos_alpha_sq = 1 - sin_alpha ** 2

        try:
            cos_2_sigma_m = cos_sigma - 2 * sin_u1 * sin_u2 / cos_alpha_sq
        except ZeroDivisionError:
            cos_2_sigma_m = 0

        c = flattening / 16 * cos_alpha_sq * (4 + flattening *
                                              (4 - 3 * cos_alpha_sq))

        prev_lambda = _lambda
        _lambda = l + (1 - c) * flattening * sin_alpha * \
                  (sigma + c * sin_sigma *
                   (cos_2_sigma_m + c *
                    cos_sigma *
                    (-1 + 2 *
                     cos_2_sigma_m ** 2)))

        if abs(_lambda - prev_lambda) < VINCENTY_CONVERGENCE_THRESHOLD:
            break

    else:
        return None

    u_sq = cos_alpha_sq * (
            EARTH_SEMI_MAJOR_AXIS ** 2 - EARTH_SEMI_MINOR_AXIS ** 2
    ) / (EARTH_SEMI_MINOR_AXIS ** 2)
    a = 1 + u_sq / 16384 * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
    b = u_sq / 1024 * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))

    delta_sigma = b * sin_sigma * (cos_2_sigma_m + b / 4 *
                                   (cos_sigma * (-1 + 2 * cos_2_sigma_m ** 2)
                                    - b / 6 * cos_2_sigma_m *
                                    (-3 + 4 * sin_sigma ** 2) *
                                    (-3 + 4 * cos_2_sigma_m ** 2)))

    s = EARTH_SEMI_MINOR_AXIS * a * (sigma - delta_sigma)
    s /= 1000  # m -> km

    return round(s, 6)


class Zone(Entity):
    def __init__(self, sm, name, latitude, longitude, radius):
        self.sm = sm
        self._name = name
        self.entity_id = name
        self._latitude = latitude
        self._longitude = longitude
        self._radius = radius

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return ZONE_STATE

    @property
    def state_attrs(self):
        attrs = {
            ATTR_LATITUDE: self._latitude,
            ATTR_LONGITUDE: self._longitude,
            ATTR_RADIUS: self._radius
        }

        return attrs