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


def resolve_config(config_path):
    app_data = os.getenv("APPDATA") if os.name == 'nt' \
        else os.path.expanduser("~")
    config_dir = os.path.join(app_data, CONFIG_DIRNAME)
    config_path = os.path.join(config_dir, config_path)

    return config_dir, config_path


def ensure_config():
    config_dir, config_path = resolve_config(DEFAULT_CONFIG_PATH)

    if os.path.exists(config_path):
        # Config exists.
        return config_path

    try:
        if not os.path.isdir(config_dir):
            os.mkdir(config_dir)
    except OSError:
        print("Could not create config directory. Try again or create one "
              f"manually at: {config_dir}")

    try:
        generate_config_defaults(config_path)
        choice = input("Do you want to configure libtracker now? [Y/n] >>> ")
        if choice.lower() == 'n':
            return config_path
        do_config_flow("Configure libtracker for first time use.",
                       fields={"latitude": "Enter latitude", "longitude": "Enter longitude",
                               "home_name": "Enter the name for your home",
                               "apple_username": "Enter your AppleID email",
                               "apple_password": "enter your AppleID password"},
                       fp=config_path)
    except (OSError, IOError):
        print(f"Could not create a config file at {config_path} try creating "
              "one manually.")

    return config_path


def generate_config_defaults(config_path):
    try:
        with open(config_path, 'w+') as f:
            json.dump(CONFIG_DEFAULTS, f)
    except:
        raise


def load_config(fp):
    try:
        with open(fp, 'r') as f:
            config = json.load(f)
    except IOError:
        print("Could not load config file. Exiting program.")
        exit(1)

    return config


def do_config_flow(description, fields, fp):
    """
    Execute a config flow. The config is stored at fp
    """
    if fields is None:
        fields = {}

    config = {}
    print(description)
    for k, v in fields.items():
        f_input = input(f'{v}: >>> ')
        config[k] = f_input

    with open(fp, 'w+') as f:
        json.dump(config, f)
