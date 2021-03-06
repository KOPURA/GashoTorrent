from threading import Thread
import time
import logging


class DataProducer(Thread):
    """
    This thread is the worker thread, which puts the information about
    all the torrents that are currently in session in the session's
    info queue. This information is later used by UI's worker thread
    in order to be displayed on the screen.
    """

    STATES = ['Queued', 'Checking', 'Downloading metadata', 'Downloading',
              'Finished', 'Seeding', 'Allocating', 'Checking fastresume']

    def __init__(self, session, timeout=2, wait_on_tick=0.2):
        super().__init__()

        self.session = session
        self.timeout = timeout
        self.wait_on_tick = wait_on_tick

    def run(self):
        while self.session.is_alive():
            torrents = self.session.get_torrents()
            if not torrents:
                time.sleep(self.timeout)
                continue

            self.session.data_queue.set_limit(len(torrents))

            if self.session.data_queue.free_slots() < len(torrents):
                time.sleep(self.timeout)
                continue

            for torrent in torrents:
                data = {}
                status = torrent.status()

                data['hash'] = torrent.info_hash()
                data['name'] = torrent.name()
                data['down_speed'] = status.download_rate
                data['up_speed'] = status.upload_rate
                data['progress'] = status.progress
                data['size'] = status.total_wanted
                data['downloaded'] = status.total_download
                data['uploaded'] = status.total_upload
                if status.paused:
                    data['state'] = 'Paused'
                else:
                    data['state'] = self.STATES[status.state]

                self.session.data_queue.push(data)

            time.sleep(self.wait_on_tick)

        logging.info("Exiting the data producer...")
