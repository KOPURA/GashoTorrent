from PyQt5.QtWidgets import (QDialog,
                             QGridLayout,
                             QHBoxLayout,
                             QLayout,
                             QLineEdit,
                             QLabel,
                             QPushButton,
                             QCheckBox)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import pyqtSignal
from core.util import Utility
import json


class SettingsDialog(QDialog):
    dataReady = pyqtSignal(dict)

    def __init__(self, parent, config):
        super().__init__(parent)

        self.config = config
        self.setUp()

    def setUp(self):
        self.setWindowTitle("Settings")
        self.setSizeGripEnabled(False)

        self.layout = QGridLayout(self)
        self.layout.setSizeConstraint(QLayout.SetFixedSize)

        # ---------------------------------------------------------------------
        portValidator = QIntValidator(self)
        portValidator.setTop(65536)
        portValidator.setBottom(0)

        self.portStartEdit = QLineEdit(str(self.config['port_start']), self)
        self.portStartEdit.setValidator(portValidator)
        self.portEndEdit = QLineEdit(str(self.config['port_end']), self)
        self.portEndEdit.setValidator(portValidator)

        portsLayout = QHBoxLayout()
        portsLayout.addWidget(self.portStartEdit)
        portsLayout.addWidget(self.portEndEdit)
        self.layout.addWidget(QLabel("Listen port range:", self), 0, 0)
        self.layout.addLayout(portsLayout, 0, 1)
        # ---------------------------------------------------------------------
        speedValidator = QIntValidator(self)
        speedValidator.setBottom(0)

        maxDownloadSpeed = str(round(self.config['max_download_speed'] / 1024))
        maxUploadSpeed = str(round(self.config['max_upload_speed'] / 1024))
        self.maxDownSpeedEdit = QLineEdit(maxDownloadSpeed, self)
        self.maxDownSpeedEdit.setValidator(speedValidator)
        self.maxUpSpeedEdit = QLineEdit(maxUploadSpeed, self)
        self.maxUpSpeedEdit.setValidator(speedValidator)

        self.layout.addWidget(QLabel("Maximum download speed (KB/s):", self),
                              1, 0)
        self.layout.addWidget(self.maxDownSpeedEdit, 1, 1)
        self.layout.addWidget(QLabel("Maximum upload speed (KB/s):", self),
                              2, 0)
        self.layout.addWidget(self.maxUpSpeedEdit, 2, 1)
        # ---------------------------------------------------------------------
        torrentCountValidator = QIntValidator(self)
        torrentCountValidator.setTop(50)
        torrentCountValidator.setBottom(2)

        self.torrentCountEdit = QLineEdit(str(self.config['max_torrents']),
                                          self)
        self.torrentCountEdit.setValidator(torrentCountValidator)

        self.layout.addWidget(QLabel("Maximal torrent count:", self), 3, 0)
        self.layout.addWidget(self.torrentCountEdit, 3, 1)
        # ---------------------------------------------------------------------
        activeTorrentsValidator = QIntValidator(self)
        activeTorrentsValidator.setBottom(0)

        self.maxActiveDownloadsEdit = QLineEdit(
                str(self.config['max_active_downloads']), self)
        self.maxActiveDownloadsEdit.setValidator(activeTorrentsValidator)
        self.maxActiveSeedsEdit = QLineEdit(
                str(self.config['max_active_seeds']), self)
        self.maxActiveSeedsEdit.setValidator(activeTorrentsValidator)

        self.layout.addWidget(QLabel("Maximum active downloads:", self), 4, 0)
        self.layout.addWidget(self.maxActiveDownloadsEdit, 4, 1)
        self.layout.addWidget(QLabel("Maximum active seeds:", self), 5, 0)
        self.layout.addWidget(self.maxActiveSeedsEdit, 5, 1)
        # ---------------------------------------------------------------------
        self.resumeDataCheckbox = QCheckBox(self)
        self.resumeDataCheckbox.setChecked(self.config['resume_data'] == 1)

        self.layout.addWidget(QLabel("Enable resume data:", self), 6, 0)
        self.layout.addWidget(self.resumeDataCheckbox, 6, 1)
        # ---------------------------------------------------------------------
        buttonsRow = QHBoxLayout()

        OKButton = QPushButton("Apply", self)
        OKButton.setFocus()
        OKButton.clicked.connect(self.accept)

        cancelButton = QPushButton("Cancel", self)
        cancelButton.clicked.connect(self.reject)

        buttonsRow.addWidget(OKButton)
        buttonsRow.addWidget(cancelButton)
        self.layout.addLayout(buttonsRow, 7, 1)

    def accept(self):
        newPortStart = int(self.portStartEdit.text())
        newPortEnd = int(self.portEndEdit.text())
        newMaxDownloadSpeed = int(self.maxDownSpeedEdit.text())
        newMaxUploadSpeed = int(self.maxUpSpeedEdit.text())
        newMaxTorrentCount = int(self.torrentCountEdit.text())
        newMaxActiveDownloads = int(self.maxActiveDownloadsEdit.text())
        newMaxActiveSeeds = int(self.maxActiveSeedsEdit.text())
        newEnableResumeData = 1 if self.resumeDataCheckbox.isChecked() else 0

        newConfig = {'port_start': newPortStart,
                     'port_end': newPortEnd,
                     'max_download_speed': newMaxDownloadSpeed * 1024,
                     'max_upload_speed': newMaxUploadSpeed * 1024,
                     'max_torrents': newMaxTorrentCount,
                     'max_active_downloads': newMaxActiveDownloads,
                     'max_active_seeds': newMaxActiveSeeds,
                     'resume_data': newEnableResumeData}

        self.hide()
        self.dataReady.emit(newConfig)
        super().accept()
