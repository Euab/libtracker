# libtracker

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

The config file is currently located in the same directory as where the Python package is installed, in future, this will be moved to the system's default configuration directory i.e. `APPDATA` or `~`.
```json
{
  "latitude": 0,
  "longitude": 0,
  "home_name": "Home"
}
```

Run:
```bash
$ python3 -m libtracker start
```