from PyQt5.QtWidgets import (QDialog,
                             QVBoxLayout,
                             QHBoxLayout,
                             QGridLayout,
                             QFileDialog,
                             QLabel,
                             QPushButton,
                             QButtonGroup,
                             QComboBox,
                             QTreeWidget,
                             QTreeWidgetItem,
                             QLineEdit)
from PyQt5.QtCore import Qt, QStandardPaths as paths
from core import file_tree
from math import log, floor
    

class TreeNodeItem(QTreeWidgetItem):
    def __init__(self, root, *args):
        super().__init__(*args)

        self.setText(0, root.path)
        self.setText(1, self.processSize(root.size))
        self.setText(2, 'Normal')

        if not root.is_leaf():
            self.setFlags(self.flags() | Qt.ItemIsTristate)

        self.setCheckState(0, Qt.Checked)

        for child in root.children:
            self.addChild(TreeNodeItem(child))

    def processSize(self, size):
        suffixes = ['KB', 'MB', 'GB', 'TB', 'PB']
        if size:
            power = floor(log(size, 1024))
            return str(round(size / 1024**power, 2)) + suffixes[power - 1]
        else:
            return "0 KB"
        

class TorrentPreferencesDialog(QDialog):
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
        defaultDir = paths.writableLocation(paths.DownloadLocation)
        torrentName = self.torrentInfo.name()

        # Show the torrent name row
        nameLabel = QLabel("Torrent name:")
        headerLayout.addWidget(nameLabel, 0, 0)

        nameEdit = QLineEdit(torrentName)
        nameEdit.setReadOnly(True)
        headerLayout.addWidget(nameEdit, 0, 1)

        # Show the destination folder row
        dirLabel = QLabel("Destination folder:")
        headerLayout.addWidget(dirLabel, 1, 0)

        self.textField = QLineEdit(defaultDir)
        self.textField.setReadOnly(True)
        headerLayout.addWidget(self.textField, 1, 1)

        button = QPushButton("Browse")
        button.clicked.connect(self.selectFolder)
        headerLayout.addWidget(button, 1, 2)

        self.layout.addLayout(headerLayout)

    def selectFolder(self):
        newDir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if newDir:
            self.textField.setText(newDir)


    def setUpFileLister(self):
        files = [(f.path, f.size) for f in self.torrentInfo.files()]
        treeView = QTreeWidget()
        treeView.setColumnCount(3)
        treeView.setColumnWidth(0, 350)
        treeView.setColumnWidth(1, 80)
        treeView.setHeaderLabels(["Name", "size", "Priority"])

        if len(files) == 1:
            tree = file_tree.FileTree(files[0][0], files[0][1])
        else:
            tree = file_tree.FileTree(files[0][0].split('/')[0], 0)
            for f in files:
                tree.add_file(f[0], f[1])
        
        rootItem = TreeNodeItem(tree.get_root())
        treeView.addTopLevelItem(rootItem)
        treeView.expandAll()
        treeView.itemClicked.connect(self.rowClicked)
        # TO DO: Add whole torrent priority combo box
        # TO DO: Add fetch data method
        # TO DO: Add some controls for checking and unchecking all of the files
        self.layout.addWidget(treeView)

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
            if  self.allChildrenHaveSamePriority(parent):
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
        priorityComboBox = QComboBox()
        priorityComboBox.addItems(["High", "Normal", "Low"])
        footerLayout.addWidget(priorityComboBox, 0, 2)

        secondRowLayout = QHBoxLayout()

        OKButton = QPushButton("Open")
        OKButton.clicked.connect(self.accept)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        secondRowLayout.addWidget(OKButton)
        secondRowLayout.addWidget(cancelButton)
        footerLayout.addLayout(secondRowLayout, 1, 2)

        self.layout.addLayout(footerLayout)

    def accept(self):
        print("Accepted") # To be implemented
        super().accept()
