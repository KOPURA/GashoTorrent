from libtorrent import bdecode, torrent_info
import urllib.request


class InfoGetter:
    """
    A 'static' class, used for getting the raw torrent file bytes
    and converting them to torrent_info objects. It supports getting
    data from the hard disk or from an url to the .torrent file.
    """
    @classmethod
    def get_bytes_from_filesystem(cls, torrent_file_name):
        result = None
        with open(torrent_file_name, "rb") as torrent_file:
            result = cls.__get_torrent_info(torrent_file.read())

        return result

    @classmethod
    def get_bytes_from_URL(cls, torrent_file_URL):
        result = None
        with urllib.request.urlopen(torrent_file_URL) as torrent_file:
            result = cls.__get_torrent_info(torrent_file.read())

        return result

    @staticmethod
    def __get_torrent_info(torrent_bytes):
        result = None

        decoded = bdecode(torrent_bytes)
        if decoded:
            result = torrent_info(decoded)
            files = result.files()

        return result
