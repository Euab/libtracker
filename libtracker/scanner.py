from typing import Tuple, Optional, Any

import click
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudNoDevicesException
from time import sleep

from libtracker.constants import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_ATTRS,
    CONFIG_APPLE_ID_USERNAME,
    CONFIG_APPLE_ID_PASSWORD
)
from libtracker.entity import Entity
from libtracker.zone import inverse_vincenty, in_zone
from libtracker.notify import send_notification

STATE_HOME = "home"
STATE_AWAY = "away"

DEFAULT_SCAN_INTERVAL = 15

DEVICE_STATUS_SET = ['features', 'maxMsgChar', 'darkWake', 'fmlyShare',
                     'deviceStatus', 'remoteLock', 'activationLocked',
                     'deviceClass', 'id', 'deviceModel', 'rawDeviceModel',
                     'passcodeLength', 'canWipeAfterLock', 'trackingInfo',
                     'location', 'msg', 'batteryLevel', 'remoteWipe',
                     'thisDevice', 'snd', 'prsId', 'wipeInProgress',
                     'lowPowerMode', 'lostModeEnabled', 'isLocating',
                     'lostModeCapable', 'mesg', 'name', 'batteryStatus',
                     'lockedTimestamp', 'lostTimestamp', 'locationCapable',
                     'deviceDisplayName', 'lostDevice', 'deviceColor',
                     'wipedTimestamp', 'modelDisplayName', 'locationEnabled',
                     'isMac', 'locFoundEnabled']


class Device(Entity):
    """ Class to represent a tracked device entity. """

    gps: Optional[Tuple[float, float]] = None
    location_name: Optional[str] = None

    _notified: bool = False
    _notified_since_last_home: bool = False

    def __init__(self, sm, device, name, config) -> None:
        self.sm = sm
        self.device = device
        self.entity_id = "device." + name
        self.config = config
        self.battery = None
        self._name = name
        self._state = None
        self._attrs = {}

    @property
    def name(self) -> str:
        """ Return the name of the device """
        return self._name

    @property
    def state(self) -> str:
        """ Return the state of the device. """
        return self._state

    @property
    def state_attrs(self) -> dict[Any]:
        """ Return a dictionary of device attributes """
        attrs = {
            ATTR_LATITUDE: self.gps[0],
            ATTR_LONGITUDE: self.gps[1]
        }

        if self._attrs:
            attrs[ATTR_ATTRS] = self._attrs

        return attrs

    def update(self) -> None:
        """ Update the device entity with data from the iCloud tracker. """
        if self.location_name:
            self._state = self.location_name

        if self.gps is not None:
            # Fetch the home zone entity from the state machine.
            h_zone = self.sm.get("zone.home")
            # Is the device home?
            zone_state = in_zone(h_zone, self.gps[0], self.gps[1], 7)
            if zone_state:
                # The device is home.
                self._state = STATE_HOME
                if not self._notified_since_last_home:
                    # If we haven't sent a Telegram since the device returned home
                    # do so now.
                    send_notification(self.name, self.config)
                self._notified_since_last_home = True
            else:
                # The device is not home.
                self._state = STATE_AWAY
                self._notified_since_last_home = False

        else:
            self._state = STATE_AWAY

        # Update state machine.
        self.push_state()

    def mark_seen(self, device_name: str, location_name: str,
                  gps: Tuple[float, float], battery: float,
                  attrs: dict[Any]) -> None:
        """ Mark a device as seen by the iCloud scanner. """
        self._name = device_name
        self.location_name = location_name

        if battery:
            self.battery = battery
        if attrs:
            self._attrs.update(attrs)

        if gps is not None:
            self.gps = float(gps[0]), float(gps[1])

        self.update()


class ICloudDeviceScanner:
    """ Class to represent an iCloud device scanner. """
    def __init__(self, sm, config) -> None:
        self._sm = sm
        self.config = config
        self.__username = config[CONFIG_APPLE_ID_USERNAME]
        self.__password = config[CONFIG_APPLE_ID_PASSWORD]
        self.api = PyiCloudService(self.__username, self.__password)
        self.devices = {}
        self._first_iter = True

        self.running = False

    def start(self) -> None:
        """ Start the scanner """
        if self.api.requires_2fa:
            self.do_icloud_2fa()

        self.add_devices()

        self.keep_alive()

    def keep_alive(self) -> None:
        """
        Keep the loop running.
        :return: None
        """
        while self.running:
            for device in self.devices:
                self.update(self.devices[device])
            sleep(DEFAULT_SCAN_INTERVAL)

            if self._first_iter:
                self._first_iter = False

    def do_icloud_2fa(self) -> None:
        devices = self.api.trusted_devices
        fmt_devices = []
        for i, device in enumerate(self.api.trusted_devices):
            fmt_devices.append("{} {}".format(i, device.get(
                "deviceName", "SMS to {}".format(
                    device.get("phoneNumber")
                )
            )))

        print(fmt_devices)

        device = click.prompt("What device do you want to perform 2FA on?",
                              default=0)
        device = devices[device]

        if not self.api.send_verification_code(device):
            print("Failed to send verification code.")
            exit(1)

        code = click.prompt("Please enter validation code.")
        if not self.api.validate_verification_code(device, code):
            self.do_icloud_2fa()

    def add_devices(self) -> None:
        for device in self.api.devices:
            status = device.status(DEVICE_STATUS_SET)
            devicename = status["name"].replace(' ', '', 99)
            device = Device(self._sm, device, devicename, self.config)
            self.devices[devicename] = device
            self.running = True

    def determine_distance(self, latitude: float, longitude: float) -> float:
        h_zone = self._sm.get("zone.home")
        zone_state_lat = h_zone.attrs[ATTR_LATITUDE]
        zone_state_lon = h_zone.attrs[ATTR_LONGITUDE]

        distance = inverse_vincenty(
            (float(latitude), float(longitude)),
            (float(zone_state_lat), float(zone_state_lon))
        )

        return distance  # km

    def update(self, device_o: Device) -> None:
        try:
            for device in self.api.devices:
                if str(device) != str(device_o.device):
                    continue

                print("Updating location for: " + str(device))

                status = device.status(DEVICE_STATUS_SET)
                location = status['location']
                battery = status.get('batteryLevel', 0) * 100

                if location:
                    distance = self.determine_distance(location[ATTR_LATITUDE],
                                                       location[ATTR_LONGITUDE])
                    print(f"Device is {str(distance)}km from home.")

                    gps = location[ATTR_LATITUDE], location[ATTR_LONGITUDE]
                    self.devices[device_o.name].mark_seen(device_o.name, "Test",
                                                          gps, battery, None)
                    self.devices[device_o.name].push_state()

        except PyiCloudNoDevicesException:
            print("No devices found.")
