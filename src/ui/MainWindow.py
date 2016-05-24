from ui.settings import Settings
from PyQt5 import Qt


class MainWindow(Qt.QMainWindow):
    def __init__(self, session):
        super().__init__()

        self.session = session
        self.setUp()

    def setUp(self):
        self.setWindowTitle(Settings.WINDOW_NAME)
        self.setGeometry(300, 300, 760, 520)
        
        self.
        
    def setUpMenuBar(self):

