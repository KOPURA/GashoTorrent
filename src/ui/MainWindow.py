from ui.settings import Settings
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    def __init__(self, session):
        super().__init__()

        self.session = session
        self.setUp()
        self.show()

    def setUp(self):
        self.setWindowTitle(Settings.WINDOW_NAME)
        self.setGeometry(600, 300, 760, 520)
        
        self.setUpMenuBar()
        
    def setUpMenuBar(self):
        menuBar = self.menuBar()

        # Create 'File' menu
        fileMenu = menuBar.addMenu("&File")
        fileMenu.setFocusPolicy(Qt.NoFocus)

        openTorrentAction = fileMenu.addAction("&Open Torrent")
        # Implement in core -  openTorrentAction.triggered.aaddAction()
        exitAction = fileMenu.addAction("&Exit")
        exitAction.triggered.connect(self.close)
        
        editMenu = menuBar.addMenu("&Edit")
        editMenu.setFocusPolicy(Qt.NoFocus)

        
