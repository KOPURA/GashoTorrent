from ui.settings import Settings
from ui.torrent_settings_dialog import TorrentPreferencesDialog
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, 
                             QFileDialog,
                             QInputDialog)
import logging


class MainWindow(QMainWindow):
    def __init__(self, width, height, desktop, main_session):
        super().__init__()

        self.session = main_session
        self.desktop = desktop

        self.setUp(width, height)
        self.show()

    def setUp(self, width, height):
        self.setWindowTitle(Settings.WINDOW_NAME)

        screen = self.desktop.screenGeometry()
        topLeftX = int(screen.width() / 2) - int(width / 2)
        topLeftY = int(screen.height() / 2) - int(height / 2)

        self.setGeometry(topLeftX, topLeftY, width, height)

        self.setUpMenuBar()
        # TO DO : Set Icon
        
    def setUpMenuBar(self):
        menuBar = self.menuBar()

        # Create 'File' menu
        fileMenu = menuBar.addMenu("&File")
        fileMenu.setFocusPolicy(Qt.NoFocus)

        openTorrentAction = fileMenu.addAction("&Open Torrent")
        openTorrentAction.triggered.connect(self.openTorrentDialog)
        openTorrentAction.setShortcut("Ctrl+O")

        openFromUrl = fileMenu.addAction("&Open from URL")
        openFromUrl.triggered.connect(self.openTorrentFromURL)
        openFromUrl.setShortcut("Ctrl+U")

        exitAction = fileMenu.addAction("&Exit")
        exitAction.triggered.connect(self.close)
        exitAction.setShortcut("Ctrl+Q")

        editMenu = menuBar.addMenu("&Edit")

    def openTorrentDialog(self):
        torrentFileName, fileFilter = QFileDialog.getOpenFileName(self,
                                                  "Select .torrent file",
                                                  "", "*.torrent")
        if torrentFileName:
            torrentInfo = self.session.InfoGetter.get_bytes_from_filesystem(
                                                            torrentFileName)
            self.addTorrentToSession(torrentInfo)

    def openTorrentFromURL(self):
        URL, ok = QInputDialog.getText(self, "Enter torrent URL",
                                       "URL of .torrent file:",)

        if ok and URL:
            torrentInfo = self.session.InfoGetter.get_bytes_from_URL(URL)
            self.addTorrentToSession(torrentInfo)

    def addTorrentToSession(self, torrentInfo):
        if torrentInfo:
            # I should have a dict of options from the pref dialog
            # including all the priorities of the files and also 
            # the priority of the whole torrent
            prefDialog = TorrentPreferencesDialog(self, torrentInfo)
            prefDialog.open()
            # TO DO : Open dialog with the files in the torrent and configure priorities
            self.session.add_torrent(torrentInfo)

    def closeEvent(self, event):
        # to do : save current session's state if it is not empty
        # in a binary file somewhere :D
        logging.info("Closing")

        self.session.destruct_session()
        event.accept()
