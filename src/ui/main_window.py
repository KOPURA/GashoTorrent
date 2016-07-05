from ui.settings import Settings
from ui.torrent_settings_dialog import TorrentPreferencesDialog
from ui.settings_dialog import SettingsDialog
from ui.ui_threads import DataConsumer
from ui.checkbox_dialog import CheckboxedMessageBox
from core.util import Utility
from core.torrent_info_getter import InfoGetter
from core.exceptions import TorrentListFullException
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (QMessageBox,
                             QMainWindow,
                             QFileDialog,
                             QInputDialog,
                             QTreeWidget,
                             QTreeWidgetItem,
                             QLabel)
import logging
import os
from enum import Enum


class QueueMovements(Enum):
    Top = 1
    Up = 2
    Down = 3
    Bottom = 4


class MainTable(QTreeWidget):
    def __init__(self, *args):
        super().__init__(*args)

        # self.indices = {}
        self.indices = []

    def addItem(self, item, itemHash):
        self.addTopLevelItem(item)
        # self.indices[itemHash] = self.topLevelItemCount() - 1
        self.indices.append(itemHash)

    def addItemAt(self, item, itemHash, pos):
        self.indices.insert(pos, itemHash)
        self.insertTopLevelItem(pos, item)

    def getIndex(self, itemHash):
        return self.indices.index(itemHash)

    def removeItem(self, itemHash):
        index = self.getIndex(itemHash)
        self.indices.pop(index)

        return self.takeTopLevelItem(index)

    def getItemFromHash(self, itemHash):
        try:
            return self.topLevelItem(self.getIndex(itemHash))
        except:
            return None

    def getHashFromIndex(self, index):
        try:
            return self.indices[index]
        except:
            return None

    def getSelectedItemIndex(self):
        return self.currentIndex().row()

    def moveItem(self, itemHash, pos):
        if pos < 0 or pos >= len(self.indices):
            return

        item = self.removeItem(itemHash)
        self.addItemAt(item, itemHash, pos)
        self.setCurrentItem(item)


class MainWindow(QMainWindow):
    def __init__(self, desktop, main_session):
        super().__init__()

        self.session = main_session
        self.desktop = desktop

        self.setUp(Settings.WIDTH, Settings.HEIGHT)

        self.consumer = DataConsumer(self, self.session, 0.5, 0.1)
        self.consumer.dataReceived.connect(self.updateTable)
        self.consumer.start()

        self.show()

    @pyqtSlot(dict)
    def updateTable(self, data):
        mainWidget = self.centralWidget()

        item = mainWidget.getItemFromHash(data['hash'])
        if item:
            finishedStates = ['Finished', 'Seeding']

            if data['state'] in finishedStates and \
               item.text(1) not in finishedStates:
                mainWidget.moveItem(data['hash'],
                                    mainWidget.topLevelItemCount() - 1)

            item.setText(0, data['name'])
            item.setText(1, data['state'])

            if(data['progress'] < 0.0001):
                item.setText(2, "0 %")
            else:
                item.setText(2, str(round(data['progress'] * 100, 2)) + " %")

            item.setText(3, Utility.process_size(data['down_speed']) + '/S')
            item.setText(4, Utility.process_size(data['up_speed']) + '/S')

    def setUp(self, width, height):
        self.setWindowTitle(Settings.WINDOW_NAME)
        self.setAcceptDrops(True)

        screen = self.desktop.screenGeometry()
        topLeftX = int(screen.width() / 2) - int(width / 2)
        topLeftY = int(screen.height() / 2) - int(height / 2)

        self.setGeometry(topLeftX, topLeftY, width, height)

        self.setUpMenuBar()
        self.setUpMainWidget()
        # TO DO : Enable torrent add via drag and drop

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

        fileMenu.addSeparator()
        # ---------------------------------------------------------------------
        resumeAllAction = fileMenu.addAction("&Resume all")
        resumeAllAction.triggered.connect(self.resumeAll)

        pauseAllAction = fileMenu.addAction("&Pause all")
        pauseAllAction.triggered.connect(self.pauseAll)

        fileMenu.addSeparator()
        # ---------------------------------------------------------------------

        exitAction = fileMenu.addAction("&Exit")
        exitAction.triggered.connect(self.close)
        exitAction.setShortcut("Ctrl+Q")

        # Create 'Edit' menu
        editMenu = menuBar.addMenu("&Edit")
        editMenu.setFocusPolicy(Qt.NoFocus)

        settingsMenu = editMenu.addAction("&Preferences")
        settingsMenu.triggered.connect(self.showSettingsDialog)
        settingsMenu.setShortcut("Ctrl+T")

        # Create 'Torrent' menu
        self.torrentMenu = menuBar.addMenu("&Torrent")
        self.torrentMenu.setFocusPolicy(Qt.NoFocus)
        self.torrentMenu.aboutToShow.connect(self.showTorrentMenu)

        togglePauseAction = self.torrentMenu.addAction("&Resume/Pause torrent")
        togglePauseAction.triggered.connect(self.togglePause)
        togglePauseAction.setShortcut("Ctrl+P")

        removeTorrentAction = self.torrentMenu.addAction("&Remove torrent")
        removeTorrentAction.triggered.connect(self.removeTorrents)
        removeTorrentAction.setShortcut("Ctrl+R")

        self.torrentMenu.addSeparator()
        # ---------------------------------------------------------------------
        moveToTopAction = self.torrentMenu.addAction("&Move to " +
                                                     "top of the queue")
        moveToTopAction.triggered.connect(self.moveToTop)

        moveUpAction = self.torrentMenu.addAction("&Move up the queue")
        moveUpAction.triggered.connect(self.moveUp)

        moveDownAction = self.torrentMenu.addAction("&Move down the queue")
        moveDownAction.triggered.connect(self.moveDown)

        moveToBottomAction = self.torrentMenu.addAction("&Move to bottom " +
                                                        "of the queue")
        moveToBottomAction.triggered.connect(self.moveToBottom)

    def setUpMainWidget(self):
        mainWidget = MainTable(self)
        mainWidget.setColumnCount(5)
        mainWidget.setColumnWidth(0, 370)
        mainWidget.setColumnWidth(1, 130)
        mainWidget.setHeaderLabels(['Name', 'State',
                                    'Progress', 'Down', 'Up'])

        self.setCentralWidget(mainWidget)

    # Add drag and drop functionality
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                torrentInfo = InfoGetter.get_bytes_from_filesystem(path)
                self.configureTorrent(torrentInfo)

    def openTorrentDialog(self):
        torrentFileName, fileFilter = QFileDialog. \
                getOpenFileName(self, "Select .torrent file", "", "*.torrent")
        if torrentFileName:
            torrentInfo = InfoGetter.get_bytes_from_filesystem(
                                                            torrentFileName)
            self.configureTorrent(torrentInfo)

    def openTorrentFromURL(self):
        URL, ok = QInputDialog.getText(self, "Enter torrent URL",
                                       "URL of .torrent file:",)

        if ok and URL:
            torrentInfo = InfoGetter.get_bytes_from_URL(URL)
            self.configureTorrent(torrentInfo)

    def configureTorrent(self, torrentInfo):
        if torrentInfo:
            prefDialog = TorrentPreferencesDialog(self, torrentInfo)
            prefDialog.dataReady.connect(self.addTorrentToSession)
            prefDialog.open()

    def addTorrentToSession(self, data):
        try:
            info_hash = self.session.add_torrent(data)
            if info_hash:
                mainWidget = self.centralWidget()

                item = QTreeWidgetItem(mainWidget)
                mainWidget.addItem(item, info_hash)
            else:
                QMessageBox.warning(self, "Error!",
                                          "Error while adding torrent file.")
        except TorrentListFullException as e:
            QMessageBox.warning(self, "Error!", "Torrent list is full.")
        except RuntimeError as e:
            stringException = str(e)
            if stringException == "torrent already exists in session":
                QMessageBox.warning(self, "Error!", "Torrent already added.")
            else:
                logging.error(str(e))

    def pauseAll(self):
        self.session.pause()

    def resumeAll(self):
        self.session.resume()

    def showSettingsDialog(self):
        self.settingsDialog = SettingsDialog(self, self.session.get_config())
        self.settingsDialog.dataReady.connect(self.reconfigureSession)
        self.settingsDialog.open()

    def reconfigureSession(self, newConfig):
        self.session.reconfigure(newConfig)

    def showTorrentMenu(self):
        mainWidget = self.centralWidget()
        enabled = not (len(mainWidget.selectedItems()) == 0)
        for action in self.torrentMenu.actions():
            action.setEnabled(enabled)

    def getHandleFromSelectedItem(self):
        mainWidget = self.centralWidget()

        currentIndex = mainWidget.getSelectedItemIndex()
        if currentIndex != -1:
            currentHash = mainWidget.getHashFromIndex(currentIndex)
            torrentHandle = self.session.getHandleFromHash(currentHash)

            return torrentHandle

        return None

    def togglePause(self):
        torrentHandle = self.getHandleFromSelectedItem()
        self.session.toggle_pause(torrentHandle)

    def removeTorrents(self):
        torrentHandle = self.getHandleFromSelectedItem()
        question = CheckboxedMessageBox(self, "Remove torrent?",
                                              "Are you sure that you want " +
                                              "to remove this torrent?",
                                              "Also remove downloaded files?")

        answer = question.exec_()
        if torrentHandle and answer[0]:
            mainWidget = self.centralWidget()
            mainWidget.removeItem(torrentHandle.info_hash())

            self.session.remove_torrent(torrentHandle, answer[1])

    def moveItem(self, movement):
        torrentHandle = self.getHandleFromSelectedItem()
        if torrentHandle:
            mainWidget = self.centralWidget()
            info_hash = torrentHandle.info_hash()
            index = mainWidget.getIndex(info_hash)

            if movement == QueueMovements.Top:
                mainWidget.moveItem(info_hash, 0)
                torrentHandle.queue_position_top()
            elif movement == QueueMovements.Up:
                mainWidget.moveItem(info_hash, index - 1)
                torrentHandle.queue_position_up()
            elif movement == QueueMovements.Down:
                mainWidget.moveItem(info_hash, index + 1)
                torrentHandle.queue_position_down()
            elif movement == QueueMovements.Bottom:
                mainWidget.moveItem(info_hash,
                                    mainWidget.topLevelItemCount() - 1)
                torrentHandle.queue_position_bottom()

    def moveToTop(self):
        self.moveItem(QueueMovements.Top)

    def moveUp(self):
        self.moveItem(QueueMovements.Up)

    def moveDown(self):
        self.moveItem(QueueMovements.Down)

    def moveToBottom(self):
        self.moveItem(QueueMovements.Bottom)

    def closeEvent(self, event):
        logging.info("Closing...")

        self.session.destruct_session()
        self.consumer.wait()
        event.accept()
