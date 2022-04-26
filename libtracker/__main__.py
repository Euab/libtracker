from libtracker.libtracker import Bus, StateMachine, load_config
from libtracker import zone

DEFAULT_CONFIG_PATH = "config.json"


def start():
    # Instantiate bus and state machine
    bus = Bus()
    sm = StateMachine(bus)

    # Load config
    config = load_config(DEFAULT_CONFIG_PATH)

    # Define the home zone
    zone.setup_home_zone(sm, config)
    print(sm.get("zone.home").to_dict())


if __name__ == "__main__":
    start()
