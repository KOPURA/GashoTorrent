import libtorrent as lt
from core.util import Utility, SafeQueue
from core.data_producer import DataProducer
from core.exceptions import TorrentListFullException
import logging
import os


class Session(lt.session):
    """
    This class represents the main core structure. It is a little "addition"
    to libtorrent's session class, which allows easier use and integration
    with the UI, which uses it.
    """
    FINGERPRINT_ID = "GT"

    def __init__(self, config_file_path):
        fingerprint = lt.fingerprint(self.FINGERPRINT_ID, 1, 0, 1, 1)
        super().__init__(fingerprint)

        self.alive = True
        self.config_file_path = config_file_path
        self.config = Utility.load_config_file(config_file_path)

        self.listen_on(self.config['port_start'], self.config['port_end'])
        self.__configure_session(self.config)

        # Initialize the data producer
        self.data_queue = SafeQueue(self.config['max_torrents'])
        self.producer = DataProducer(self, 0.5, 0.1)
        self.producer.start()

    def __configure_session(self, config):
        settings = {'download_rate_limit': config['max_download_speed'],
                    'upload_rate_limit': config['max_upload_speed'],
                    'active_downloads': config['max_active_downloads'],
                    'active_seeds': config['max_active_seeds']}
        self.apply_settings(settings)
        # Uncomment the next line to enable all alerts
        # self.set_alert_mask(0x7fffffff)

    def reconfigure(self, new_config):
        self.config = new_config
        self.__configure_session(new_config)
        self.data_queue.set_limit(new_config['max_torrents'])
        Utility.update_config_file(self.config_file_path, new_config)

    def destruct_session(self):
        if self.config['resume_data']:
            handles = list(filter(Utility.has_metadata, self.get_torrents()))
            paths = list(map(Utility.handle_fastresume_path, handles))
            data = [lt.bencode(h.write_resume_data()) for h in handles]
            for path, data in zip(paths, data):
                with open(path, "wb") as fr_file:
                    fr_file.write(data)

        self.alive = False
        self.producer.join()
        del self

    def get_config(self):
        return self.config

    def getHandleFromHash(self, hash_):
        for handle in self.get_torrents():
            if hash_ == handle.info_hash():
                return handle

        return None

    def is_alive(self):
        return self.alive

    def add_torrent(self, data):
        if len(self.get_torrents()) == self.config['max_torrents']:
            raise TorrentListFullException

        params = {'ti': data['info'],
                  'save_path': data['destination_folder'],
                  'paused': False,
                  'auto_managed': True,
                  'duplicate_is_error': True}

        path = Utility.fastresume_path(data['info'].name(),
                                       data['destination_folder'])
        try:
            params['resume_data'] = open(path, 'rb').read()
            os.remove(path)
        except:
            logging.info("No resume data for " + data['info'].name())

        handle = super().add_torrent(params)
        handle.set_priority(data['torrent_priority'])
        handle.prioritize_files(data['file_priorities'])
        if handle.is_valid():
            return handle.info_hash()

        return None

    @staticmethod
    def toggle_pause(torrent_handle):
        if torrent_handle:
            status = torrent_handle.status()
            if status.paused:
                torrent_handle.auto_managed(True)
                torrent_handle.resume()
            else:
                torrent_handle.auto_managed(False)
                torrent_handle.pause()

    def remove_torrent(self, handle, with_files=False):
        if with_files:
            super().remove_torrent(handle, lt.options_t.delete_files)
        else:
            super().remove_torrent(handle)
