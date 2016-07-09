from core.torrent_info_getter import InfoGetter
import libtorrent as lt
import unittest
import urllib.request
from os import mkdir, path
import shutil
import json


class TestInfoGetter(unittest.TestCase):
    def setUp(self):
        with open('tests/links.txt') as links:
            self.links = json.load(links)

        if not path.exists('torrents'):
            mkdir('torrents')

        for index, link in enumerate(self.links):
            with urllib.request.urlopen(link) as torrent_file:
                name = 'torrents/torrent' + str(index) + '.torrent'
                with open(name, 'wb') as disk_file:
                    disk_file.write(torrent_file.read())

    def tearDown(self):
        shutil.rmtree('torrents')

    def test_get_info_from_filesystem(self):
        for x in range(0, len(self.links)):
            self.assertIsNotNone(InfoGetter.get_bytes_from_filesystem(
                                 'torrents/torrent' + str(x) + '.torrent'))

    def test_get_info_from_url(self):
        for link in self.links:
            self.assertIsNotNone(InfoGetter.get_bytes_from_URL(link))

    def test_equivalent_infos(self):
        for index, link in enumerate(self.links):
            bytes_info = InfoGetter.get_bytes_from_filesystem(
                         'torrents/torrent' + str(index) + '.torrent')
            url_info = InfoGetter.get_bytes_from_URL(link)

            self.assertEqual(bytes_info.info_hash(), url_info.info_hash())
            self.assertEqual(bytes_info.num_files(), url_info.num_files())

            bytes_files = bytes_info.files()
            url_files = url_info.files()
            for i in range(0, len(url_files)):
                file_one = bytes_files.at(i)
                file_two = url_files.at(i)

                self.assertEqual(file_one.path, file_two.path)
                self.assertEqual(file_one.size, file_two.size)
                self.assertEqual(file_one.filehash, file_two.filehash)
