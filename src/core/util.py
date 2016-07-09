from math import floor, log
from threading import Lock
import json
import os


class Utility:
    @staticmethod
    def process_size(size):
        """
        It receives a number, which represents a size in bytes and converts
        the number to a more human-readable format as string.
        """
        suffixes = ['KB', 'MB', 'GB', 'TB', 'PB', 'B']
        if size:
            power = floor(log(size, 1024))
            if power > 5:
                power = 5
            return (str(round(size / (1024**power), 2)) + " " +
                    suffixes[power - 1])

        return "0 KB"

    @staticmethod
    def load_config_file(path):
        config = None
        try:
            with open(path) as config_file:
                config = json.load(config_file)
        except Exception as e:
            raise e

        return config

    @staticmethod
    def update_config_file(path, new_config):
        try:
            with open(path, "w") as config_file:
                json.dump(new_config, config_file)
        except Exception as e:
            raise e

    @staticmethod
    def has_metadata(handle):
        """
        Used for a predicate to filter these torrent handles, for which
        a .fastresume file should be generated.
        """
        return all([handle.is_valid(),
                   handle.has_metadata(),
                   handle.status().state > 2])

    @staticmethod
    def handle_fastresume_path(handle):
        """
        Builds the .fastresume file path of the given handle.
        """
        return Utility.fastresume_path(handle.get_torrent_info().name(),
                                       handle.save_path())

    @staticmethod
    def fastresume_path(name, save_path):
        """
        Builds the fastresume path of a torrent given its name and
        save path
        """
        return os.path.join(save_path, name + ".fastresume")


class SafeQueue:
    """
    This class represents a thread-safe queue structure. It is used for
    the communication between the core's worker thread and the UI's worker
    thread.
    """
    def __init__(self, limit):
        self.data = []

        self.lock = Lock()
        self.limit = limit
        self.count = 0

    def set_limit(self, new_limit):
        with self.lock:
            self.limit = new_limit

    def pop(self):
        element = None

        if self.count > 0:
            self.count -= 1
            with self.lock:
                element = self.data.pop(0)

        return element

    def push(self, data):
        if self.count < self.limit:
            self.count += 1
            with self.lock:
                if self.count == 0:
                    self.data.insert(0, data)
                else:
                    self.data.append(data)

    def empty(self):
        return self.count == 0

    def full(self):
        with self.lock:
            return self.count == self.limit

    def free_slots(self):
        with self.lock:
            return self.limit - self.count

    def get_limit(self):
        with self.lock:
            return self.limit
