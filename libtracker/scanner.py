import click
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudNoDevicesException
from time import sleep
from datetime import datetime

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


class ICloudDeviceScanner:
    def __init__(self, sm, config):
        self._sm = sm
        self.config = config
        self.__username = config[CONFIG_APPLE_ID_USERNAME]
        self.__password = config[CONFIG_APPLE_ID_PASSWORD]
        self.api = PyiCloudService(self.__username, self.__password)
        self.devices = {}
        self._first_iter = True

        self.running = False

    def start(self):
        if self.api.requires_2fa:
            self.do_icloud_2fa()

        self.add_devices()

        self.keep_alive()

    def keep_alive(self):
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

    def do_icloud_2fa(self):
        devices = self.api.trusted_devices
        print(devices)
        fmt_devices = []
        for i, device in enumerate(self.api.trusted_devices):
            devices.append("{} {}".format(i, device.get(
                "deviceName", "SMS to {}".format(
                    device.get("phoneNumber")
                )
            )))

        print(fmt_devices)

        device = click.prompt("What device do you want to perform 2FA on?", default=0)
        device = devices[device]

        if not self.api.send_verification_code(device):
            print("Failed to send verification code.")
            exit(1)

        code = click.prompt("Please enter validation code.")
        if not self.api.validate_verification_code(device, code):
            self.do_icloud_2fa()

    def add_devices(self):
        for device in self.api.devices:
            status = device.status(DEVICE_STATUS_SET)
            devicename = status["name"].replace(' ', '', 99)
            device = Device(self._sm, device, devicename, self.config)
            self.devices[devicename] = device
            self.running = True

    def determine_distance(self, latitude, longitude):
        h_zone = self._sm.get("zone.home")
        zone_state_lat = h_zone.attrs[ATTR_LATITUDE]
        zone_state_lon = h_zone.attrs[ATTR_LONGITUDE]

        distance = inverse_vincenty(
            (float(latitude), float(longitude)),
            (float(zone_state_lat), float(zone_state_lon))
        )

        return distance  # km

    def update(self, device_o):
        try:
            for device in self.api.devices:
                if str(device) != str(device_o.device):
                    continue


                status = device.status(DEVICE_STATUS_SET)
                location = status['location']
                print(location)
                battery = status.get('batteryLevel', 0) * 100

                if location:
                    distance = self.determine_distance(location[ATTR_LATITUDE],
                                                       location[ATTR_LONGITUDE])

                    gps = location[ATTR_LATITUDE], location[ATTR_LONGITUDE]
                    self.devices[device_o.name].mark_seen(device_o.name, "Test",
                                                          gps, battery, None)
                    self.devices[device_o.name].push_state()

        except PyiCloudNoDevicesException:
            print("No devices found.")


class Device(Entity):

    gps = None
    location_name = None

    _notified = False
    _notified_since_last_home = False

    def __init__(self, sm, device, name, config):
        self.sm = sm
        self.device = device
        self.entity_id = "device." + name
        self.config = config
        self.battery = None
        self._name = name
        self._state = None
        self._attrs = {}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def state_attrs(self):
        attrs = {
            ATTR_LATITUDE: self.gps[0],
            ATTR_LONGITUDE: self.gps[1]
        }

        if self._attrs:
            attrs[ATTR_ATTRS] = self._attrs

        return attrs

    def update(self):
        if self.location_name:
            self._state = self.location_name

        if self.gps is not None:
            h_zone = self.sm.get("zone.home")
            zone_state = in_zone(h_zone, self.gps[0], self.gps[1], 7)
            if zone_state:
                self._state = STATE_HOME
                if not self._notified_since_last_home:
                    send_notification(self.name, self.config)
                self._notified_since_last_home = True
            else:
                self._state = STATE_AWAY
                self._notified_since_last_home = False

        else:
            self._state = STATE_AWAY

        self.push_state()

    def mark_seen(self, device_name, location_name, gps, battery, attrs):
        self._name = device_name
        self.location_name = location_name

        if battery:
            self.battery = battery
        if attrs:
            self._attrs.update(attrs)

        if gps is not None:
            self.gps = float(gps[0]), float(gps[1])

        self.update()
