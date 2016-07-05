from math import floor, log
from threading import Lock
import json
import os


class Utility:
    @staticmethod
    def process_size(size):
        suffixes = ['KB', 'MB', 'GB', 'TB', 'PB', 'B']
        if size:
            power = floor(log(size, 1024))
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
        return handle.is_valid() and \
               handle.has_metadata() and \
               handle.status().state > 2

    @staticmethod
    def handle_fastresume_path(handle):
        return os.path.join(handle.save_path(),
                            handle.get_torrent_info().name() + ".fastresume")

    @staticmethod
    def fastresume_path(name, save_path):
        return os.path.join(save_path, name + ".fastresume")


class SafeQueue:
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
        return self.count == self.limit

    def free_slots(self):
        return self.limit - self.count
