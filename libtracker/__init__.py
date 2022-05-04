import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from typing import Union

from libtracker.state import StateMachine
from libtracker.config import ensure_config, load_config
from libtracker.scanner import ICloudDeviceScanner
from libtracker import zone

SUPPORTED_SCANNER_TYPES = ("icloud", "ios")

# Currently only have support for one scanner but more mappings can be
# easily added here.
SCANNER_MAP = {
    "ios": ICloudDeviceScanner,
    "icloud": ICloudDeviceScanner
}


# noinspection PyShadowingNames
class LibtrackerRunner:
    """
    Root class of Libtracker
    """

    running_scanners: list
    _pool: ThreadPoolExecutor

    def __init__(self, config: dict = None,
                 scanners: Union[list[str], str] = None) -> None:
        self.states = StateMachine()
        self.config = config
        self.scanners = scanners or []

    def start(self) -> None:
        """ Attempt to initialise Libtracker """
        if self.config is None:
            # If the user is running Libtracker as a script config will not be
            # passed in so set up config now.
            config_path = ensure_config()
            self.config = load_config(config_path)

        # Setup the home zone
        zone.setup_home_zone(self.states, self.config)

        if not self.scanners:
            raise RuntimeError("Scanners must contain a scanner.")
        if not isinstance(self.scanners, list):
            self.scanners = [self.scanners]

        self.running_scanners = []
        for scanner in self.scanners:
            # Map each chosen scanner to its scanner class and append to
            # the list of scanners we would like to run.
            if (scanner := scanner.lower()) in SUPPORTED_SCANNER_TYPES:
                scanner = SCANNER_MAP[scanner](self.states, self.config)
                self.running_scanners.append(scanner)

        if self.running_scanners:
            # Create a thread pool with num_threads = amount of scanners.
            self._pool = ThreadPoolExecutor(len(self.running_scanners))

            futs = []
            for scanner in self.running_scanners:
                # Start each scanner
                result = self._pool.submit(scanner.start)
                # Append the new future to an array
                futs.append(result)

            for fut in futs:
                # Add the exception callback for each future
                fut.add_done_callback(_scanner_exception_callback)


def _scanner_exception_callback(future: concurrent.futures.Future) -> None:
    """
    Add a callback which allows exceptions coming from the any futures
    set to be caught instead of the program failing quietly
    """
    print(future.result())
