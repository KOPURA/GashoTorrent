import unittest
from core.session import Session


class TestSession(unittest.TestCase):
    def setUp(self):
        self.config_file = "config/config.conf"
        self.session = Session(self.config_file)

    def test_session(self):
        self.assertTrue(self.session.is_alive())
        self.assertIsNotNone(self.session.get_config())
        self.assertTrue(self.session.is_listening())

    def test_session_settings(self):
        settings = self.session.settings()
        config = self.session.get_config()

        self.assertEqual(settings['download_rate_limit'],
                         config['max_download_speed'])
        self.assertEqual(settings['upload_rate_limit'],
                         config['max_upload_speed'])
        self.assertEqual(settings['active_downloads'],
                         config['max_active_downloads'])
        self.assertEqual(settings['active_seeds'],
                         config['max_active_seeds'])
        self.assertEqual(self.session.data_queue.get_limit(),
                         config['max_torrents'])

    def tearDown(self):
        self.session.destruct_session()
