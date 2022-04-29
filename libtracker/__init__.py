from concurrent.futures import ThreadPoolExecutor

from libtracker.state import StateMachine
from libtracker.config import ensure_config, load_config
from libtracker.scanner import ICloudDeviceScanner
from libtracker import zone

SUPPORTED_SCANNER_TYPES = ("icloud", "ios")

SCANNER_MAP = {
    "ios": ICloudDeviceScanner,
    "icloud": ICloudDeviceScanner
}


class LibtrackerRunner:
    """
    Root class of Libtracker
    """

    running_scanners = []
    _pool = None

    def __init__(self, config=None, scanners=None):
        self.states = StateMachine()
        self.config = None
        self.scanners = scanners or []

    def start(self):
        if self.config is None:
            config_path = ensure_config()
            self.config = load_config(config_path)

        zone.setup_home_zone(self.states, self.config)

        if not self.scanners:
            raise RuntimeError("Scanners must contain a scanner.")
        if not isinstance(self.scanners, list):
            self.scanners = [self.scanners]

        for scanner in self.scanners:
            print(scanner)
            if (scanner := scanner.lower()) in SUPPORTED_SCANNER_TYPES:
                scanner = SCANNER_MAP[scanner](self.states, self.config)
                self.running_scanners.append(scanner)

        print(self.running_scanners)

        if self.running_scanners:
            self._pool = ThreadPoolExecutor(len(self.running_scanners))

            for scanner in self.running_scanners:
                result = self._pool.submit(scanner.start)