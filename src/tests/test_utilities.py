import unittest
import os
from core.util import Utility


class TestUtilities(unittest.TestCase):
    def test_process_size(self):
        self.assertEqual(Utility.process_size(0), '0 KB')
        self.assertEqual(Utility.process_size(1024), "1.0 KB")
        self.assertEqual(Utility.process_size(1500000000000000000),
                         "1332.27 PB")
        self.assertEqual(Utility.process_size(1048576), "1.0 MB")
        self.assertEqual(Utility.process_size(1), "1.0 B")

    def test_fastresume_path(self):
        self.assertEqual(Utility.fastresume_path("name", "path"),
                         "path" + os.path.sep + "name.fastresume")
