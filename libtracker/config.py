import json
import os

from libtracker.constants import (
    CONFIG_DIRNAME,
    DEFAULT_CONFIG_PATH,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
)

CONFIG_DEFAULTS = {
    ATTR_LATITUDE: 0,
    ATTR_LONGITUDE: 0,
    "home_name": "Home"
}


def ensure_config():
    app_data = os.getenv("APPDATA") if os.name == 'nt' \
        else os.path.expanduser("~")
    config_dir = os.path.join(app_data, CONFIG_DIRNAME)
    config_path = os.path.join(config_dir, DEFAULT_CONFIG_PATH)

    if os.path.exists(config_path):
        # Config exists.
        return config_path

    try:
        os.mkdir(config_dir)
    except OSError:
        print("Could not create config directory. Try again or create one "
              f"manually at: {config_dir}")

    try:
        generate_config_defaults(config_path)
    except (OSError, IOError):
        print(f"Could not create a config file at {config_path} try creating "
              f"one manually. Go to https://github.com/Euab/libtracker/blob/main/README.md "
              f"for more information.")

    return config_path


def generate_config_defaults(config_path):
    try:
        with open(config_path, 'w+') as f:
            json.dump(CONFIG_DEFAULTS, f)
    except:
        raise
