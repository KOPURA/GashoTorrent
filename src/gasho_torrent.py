from PyQt5.Qt import QApplication
from ui import MainWindow
from core import session
import sys


if __name__ == '__main__':
    app = QApplication(sys.argv)
    session = session.Session()
    main_window = MainWindow.MainWindow(session)
    main_window.show()
    app.exec_()

