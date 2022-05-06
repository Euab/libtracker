# libtracker

> **MODERATORS:** redirect [here](https://github.com/Euab/libtracker/releases/tag/MODERATORS) for the state of the
> project at submission. This project is being continually developed.

Simple python library to track the GPS position of devices.

Designed to be run on a small device such as a Raspberry PI.

## Background
To derive the distances between two devices where the given device location data consists of two tuples of longitude and latitude we implement the inverse of the Vincenty formula.
This will determine the distance between two points on an assumed oblate spheroid which accurately models the Earth according to the WGS80 standard.

## Installation
Pip install:
```bash
$ python3 -m pip install git+https://github.com/Euab/libtracker.git#egg=libtracker
```

The config file is located at the system's user site. E.g. `APPDATA` or `~`.
```json
{
  "latitude": 0,
  "longitude": 0,
  "home_name": "Home",
  "apple_username": "x@example.com",
  "apple_password": "X",
  "telegram_users": ["X", "Y"],
  "telegram_token": "X"
}
```

`telegram_users` should contain a list of string Telegram user ID(s) that you want to send a notification to.
To see how to find your user ID for your Telegram account [click here.](https://www.alphr.com/telegram-find-user-id/)
`telegram_token` should contain an API key for a Telegram bot account. To find out how to make a Telegram bot account,
[click here.](https://docs.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram?view=azure-bot-service-4.0#create-a-new-telegram-bot-with-botfather)
For a more detailed overview of Telegram bots, [click here.](https://core.telegram.org/bots)
Omitting the Telegram configuration values will disable notifications.

## Running as a script
Run:
```bash
$ python3 -m libtracker
```

## Running as a class
Use the Libtracker runner class instead.

Threaded example: Print all the states inside Libtracker every 20 seconds.
```python
import threading
import time

from libtracker import LibtrackerRunner


lt = LibtrackerRunner(
    scanners="icloud",
    config={
        "latitude": 0.00,
        "longitude": 0.00,
        "home_name": "My home",
        "apple_username": "john.smith@apple.com",
        "apple_password": "X",
        "telegram_users": ["X", "Y"],
        "telegram_token": "X"
    }
)


def fetch_states():
    """
    Loop that will fetch us a list of all the states from the state machine
    every 20 seconds.
    """

    while True:
        states = lt.states.all()
        print(states)
        time.sleep(20)

        
# Run Libtracker in another thread.
t1 = threading.Thread(target=lt.start)
t1.start()

fetch_states()
```

```bash
$ python3 test.py

[{'entity_id': 'zone.home', 'state': 'zoning', 'attrs': {'latitude': 0.00, 'longitude': -0.00, 'radius': 20}}]
Updating location for: MacBook Pro 13": Euab’s MacBook Pro
Device is 0.017753km from home.
Updating location for: iPhone 7 Plus: Euab's iPhone 7 Plus
Updating location for: iPhone 12: Euab's iPhone 12
Device is 0.026815km from home.
Updating location for: MacBook Pro 13": Euab’s MacBook Pro
Device is 0.017753km from home.
Updating location for: iPhone 7 Euab's iPhone 7 Plus
Updating location for: iPhone 12: Euab's iPhone 12
Device is 0.026815km from home.
[{'entity_id': 'zone.home', 'state': 'zoning', 'attrs': {'latitude': 0.00, 'longitude': -0.00, 'radius': 20}}, {'entity_id': 'device.euab’smacbookpro', 'state': 'home', 'attrs': {'latitude': 0.00, 'longitude': -0.00}}, {'entity_id': 'device.euab’siphone12', 'state': 'home', 'attrs': {'latitude': 0.00, 'longitude': -0.00}}]
```
