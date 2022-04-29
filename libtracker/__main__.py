import threading

from state import StateMachine
from config import ensure_config, load_config

from libtracker.scanner import ICloudDeviceScanner
import zone


def start():
    # Ensure config file exists and load in config
    config_path = ensure_config()

    # Instantiate state machine
    sm = StateMachine()

    # Load config
    config = load_config(config_path)

    # Define the home zone
    zone.setup_home_zone(sm, config)

    scanner = ICloudDeviceScanner(sm, config)
    t = threading.Thread(target=scanner.start())
    t.start()


if __name__ == "__main__":
    start()
