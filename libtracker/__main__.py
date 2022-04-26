from libtracker.libtracker import Bus, StateMachine, load_config
from libtracker import zone
from libtracker.config import ensure_config


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
    print(sm.get("zone.home").to_dict())


if __name__ == "__main__":
    start()
