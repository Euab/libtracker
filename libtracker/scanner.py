import click
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudNoDevicesException
from time import sleep
from datetime import datetime

from libtracker.constants import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_RADIUS,
    CONFIG_APPLE_ID_USERNAME,
    CONFIG_APPLE_ID_PASSWORD
)
from libtracker.zone import inverse_vincenty, in_zone

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
    def __init__(self, bus, sm, config):
        self._bus = bus
        self._sm = sm
        self.config = config
        self.__username = config[CONFIG_APPLE_ID_USERNAME]
        self.__password = config[CONFIG_APPLE_ID_PASSWORD]
        self.api = PyiCloudService(self.__username, self.__password)
        self.devices = {}
        self.seen_devices = {}

        self.running = False

        if self.api.requires_2fa:
            self.do_icloud_2fa()

        self.add_devices()

        while self.running:
            try:
                self.update("GusFring")  # this is the hostname of my phone lmao
                sleep(DEFAULT_SCAN_INTERVAL)
            except KeyboardInterrupt:
                print("Ctrl-C detected: Stopping libtracker gracefully.")
                self.running = False

    def do_icloud_2fa(self):
        devices = self.api.trusted_devices
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
            print("Failed to verify verification code.")
            exit(1)

    def add_devices(self):
        for device in self.api.devices:
            status = device.status(DEVICE_STATUS_SET)
            devicename = status["name"].replace(' ', '', 99)
            self.devices[devicename] = device
            self.running = True

    def determine_distance(self, devicename, latitude, longitude, battery):
        distance_from_home = None
        h_zone = self._sm.get("zone.home")
        zone_state_lat = h_zone.attrs[ATTR_LATITUDE]
        zone_state_lon = h_zone.attrs[ATTR_LONGITUDE]

        distance = inverse_vincenty(
            (float(latitude), float(longitude)),
            (float(zone_state_lat), float(zone_state_lon))
        )

        return distance  # km

    def update(self, device_name):
        try:
            print(f"Time is: {datetime.utcnow().isoformat()}")
            for device in self.api.devices:
                print(f"Updating location for: {str(device)}")
                if str(device) != str(self.devices[device_name]):
                    print("\t- Not updating")
                    continue

                status = device.status(DEVICE_STATUS_SET)
                dev_id = status['name'].replace(' ', '', 99)
                location = status['location']
                battery = status.get('batteryLevel', 0) * 100

                if location:
                    distance = self.determine_distance(device_name, location[ATTR_LATITUDE],
                                                       location[ATTR_LONGITUDE], battery)
                    print(f"\t- Device is {distance}km from home")
                    print(f"\t- Latitude: {location[ATTR_LATITUDE]}. Longitude: {location[ATTR_LONGITUDE]}")

                    # Check if the device is home
                    h_zone = self._sm.get("zone.home")

                    is_home = in_zone(
                        h_zone,
                        float(location[ATTR_LATITUDE]), float(location[ATTR_LONGITUDE]),
                        h_zone.attrs[ATTR_RADIUS]
                    )
                    if is_home:
                        print("\t- Device is home")
                    else:
                        print("\t- Not home")

                    # Mark the device as seen
                    self.seen_devices[device_name] = True
                print("\n")

        except PyiCloudNoDevicesException:
            print("No devices found.")

