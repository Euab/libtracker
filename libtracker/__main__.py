from libtracker.libtracker import Bus, StateMachine
from libtracker import zone
from libtracker.config import ensure_config, load_config
from libtracker.scanner import ICloudDeviceScanner


def start():
    # Ensure config file exists and load in config
    config_path = ensure_config()

    # Instantiate bus and state machine
    bus = Bus()
    sm = StateMachine(bus)

    # Load config
    config = load_config(config_path)

    # Define the home zone
    zone.setup_home_zone(sm, config)

    try:
        scanner = ICloudDeviceScanner(bus, sm, config)
    except Exception as e:
        print(f"Failed to initialise icloud scanner: {e}")


if __name__ == "__main__":
    start()
