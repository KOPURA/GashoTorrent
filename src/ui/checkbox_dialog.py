from PyQt5.QtWidgets import (QMessageBox,
                             QCheckBox)


class CheckboxedMessageBox(QMessageBox):
    def __init__(self, parent,  title, text, checkboxText):
        super().__init__(parent)

        self.checkbox = QCheckBox()

        self.setWindowTitle(title)
        self.setText(text)
        self.checkbox.setText(checkboxText)
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
        self.setIcon(QMessageBox.Question)

        layout = self.layout()
        layout.addWidget(self.checkbox, 1, 2)

    def exec_(self, *args, **kwargs):
        return super().exec_(*args, **kwargs), self.checkbox.isChecked()
