from PyQt5.QtWidgets import (QDialog,
                             QVBoxLayout,
                             QHBoxLayout,
                             QGridLayout,
                             QFileDialog,
                             QLabel,
                             QPushButton,
                             QComboBox,
                             QTreeWidget,
                             QTreeWidgetItem,
                             QTreeWidgetItemIterator,
                             QLineEdit)
from PyQt5.QtCore import pyqtSignal, Qt, QStandardPaths as paths
from core import file_tree
from core.util import Utility


class TreeNodeItem(QTreeWidgetItem):
    def __init__(self, root, *args):
        super().__init__(*args)

        self.setText(0, root.path)
        self.setText(1, Utility.process_size(root.size))
        self.setText(2, 'Normal')

        if not root.is_leaf():
            self.setFlags(self.flags() | Qt.ItemIsTristate)

        self.setCheckState(0, Qt.Checked)

        for child in root.children:
            self.addChild(TreeNodeItem(child))


class TorrentPreferencesDialog(QDialog):
    dataReady = pyqtSignal(dict)

    def __init__(self, parent, torrent_info):
        super().__init__(parent)
        self.torrentInfo = torrent_info

        self.setUp()

    def setUp(self):
        self.setWindowTitle("Torrent settings")

        parentRect = self.parentWidget().geometry()
        self.resize(parentRect.width() * 0.75, parentRect.height() * 0.9)
        self.setMinimumSize(self.size())

        # Create the dialog layout
        self.layout = QVBoxLayout(self)

        # Set up the destination folder selector
        self.setUpDialogHeader()
        # Set up the file lister for the torrent file
        self.setUpFileLister()
        # Set up the whole torrent priority combo box and buttons
        self.setUpDialogFooter()

    def setUpDialogHeader(self):
        headerLayout = QGridLayout()
        self.destinationFolder = paths.writableLocation(paths.DownloadLocation)
        torrentName = self.torrentInfo.name()

        # Show the torrent name row
        nameLabel = QLabel("Torrent name:", self)
        headerLayout.addWidget(nameLabel, 0, 0)

        nameEdit = QLineEdit(torrentName, self)
        nameEdit.setReadOnly(True)
        headerLayout.addWidget(nameEdit, 0, 1)

        # Show the destination folder row
        dirLabel = QLabel("Destination folder:", self)
        headerLayout.addWidget(dirLabel, 1, 0)

        self.textField = QLineEdit(self.destinationFolder, self)
        self.textField.setReadOnly(True)
        headerLayout.addWidget(self.textField, 1, 1)

        button = QPushButton("Browse", self)
        button.clicked.connect(self.selectFolder)
        headerLayout.addWidget(button, 1, 2)

        self.layout.addLayout(headerLayout)

    def selectFolder(self):
        newDir = str(QFileDialog.getExistingDirectory(self,
                                                      "Select Directory"))
        if newDir:
            self.textField.setText(newDir)
            self.destinationFolder = newDir

    def setUpFileLister(self):
        self.files = [(f.path, f.size) for f in self.torrentInfo.files()]
        self.treeView = QTreeWidget(self)
        self.treeView.setColumnCount(3)
        self.treeView.setColumnWidth(0, 350)
        self.treeView.setColumnWidth(1, 80)
        self.treeView.setHeaderLabels(["Name", "size", "Priority"])
        self.treeView.setExpandsOnDoubleClick(False)

        if len(self.files) == 1:
            tree = file_tree.FileTree(self.files[0][0], self.files[0][1])
        else:
            tree = file_tree.FileTree(self.files[0][0].split('/')[0], 0)
            for f in self.files:
                tree.add_file(f[0], f[1])

        rootItem = TreeNodeItem(tree.get_root(), self.treeView)
        self.treeView.addTopLevelItem(rootItem)
        self.treeView.expandAll()
        self.treeView.itemClicked.connect(self.rowClicked)
        self.layout.addWidget(self.treeView)

    def rowClicked(self, item, column):
        if item.checkState(0) == Qt.PartiallyChecked:
            item.setCheckState(0, Qt.Checked)

        if column == 2:
            priorityChanges = {'Normal': 'High',
                               'High': 'Low',
                               'Low': 'Normal',
                               'Mixed': 'Normal'}
            newPriority = priorityChanges[item.text(2)]
            self.changeTextOfAllChildren(item, 2, newPriority)

            self.reprioritize(item)

    def changeTextOfAllChildren(self, item, column, text):
        item.setText(column, text)
        for i in range(0, item.childCount()):
            self.changeTextOfAllChildren(item.child(i), column, text)

    def reprioritize(self, start_node):
        parent = start_node.parent()
        if parent:
            if self.allChildrenHaveSamePriority(parent):
                parent.setText(2, start_node.text(2))
            else:
                parent.setText(2, "Mixed")

            self.reprioritize(parent)

    def allChildrenHaveSamePriority(self, node):
        for i in range(1, node.childCount()):
            if node.child(i - 1).text(2) != node.child(i).text(2):
                return False

        return True

    def setUpDialogFooter(self):
        footerLayout = QGridLayout()
        footerLayout.setColumnStretch(0, 4)

        footerLayout.addWidget(QLabel("Torrent priority"), 0, 1)
        self.priorityComboBox = QComboBox(self)
        self.priorityComboBox.addItems(["High", "Normal", "Low"])
        self.priorityComboBox.setCurrentIndex(1)
        footerLayout.addWidget(self.priorityComboBox, 0, 2)

        secondRowLayout = QHBoxLayout()

        OKButton = QPushButton("Open", self)
        OKButton.setFocus()
        OKButton.clicked.connect(self.accept)
        cancelButton = QPushButton("Cancel", self)
        cancelButton.clicked.connect(self.reject)
        secondRowLayout.addWidget(OKButton)
        secondRowLayout.addWidget(cancelButton)
        footerLayout.addLayout(secondRowLayout, 1, 2)

        self.layout.addLayout(footerLayout)

    def accept(self):
        torrentPriorities = {"Low": 0, "Normal": 127, "High": 255}
        filePriorities = {"Low": 1, "Normal": 4, "High": 7}

        it = QTreeWidgetItemIterator(self.treeView,
                                     QTreeWidgetItemIterator.NoChildren)

        itemsInfo = {}
        while it.value():
            currentItem = it.value()
            if currentItem.checkState(0) == Qt.Unchecked:
                priority = 0
            else:
                priority = filePriorities[currentItem.text(2)]

            itemsInfo[self.getFullPath(currentItem)] = priority
            it += 1

        paths = [f.path for f in self.torrentInfo.files()]
        self.prioritiesList = [itemsInfo[p] for p in paths]

        comboBoxIndex = self.priorityComboBox.currentIndex()
        self.priority = torrentPriorities[self.priorityComboBox.itemText(
                                                                comboBoxIndex)]

        self.hide()
        self.dataReady.emit(self.getData())
        super().accept()

    def getFullPath(self, treeItem):
        items = [treeItem.text(0)]
        parent = treeItem.parent()

        while parent:
            items.append(parent.text(0))
            parent = parent.parent()

        return '/'.join(reversed(items))

    def getData(self):
        return {'info': self.torrentInfo,
                'destination_folder': self.destinationFolder,
                'torrent_priority': self.priority,
                'file_priorities': self.prioritiesList}
