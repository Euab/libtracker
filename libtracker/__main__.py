from libtracker import LibtrackerRunner


if __name__ == "__main__":
    runner = LibtrackerRunner(scanners="icloud")
    runner.start()
