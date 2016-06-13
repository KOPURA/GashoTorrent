from PyQt5.Qt import QApplication
from PyQt5.QtWidgets import QMessageBox
from ui import main_window
from core import session
import sys
import logging


if __name__ == '__main__':
    app = QApplication(sys.argv)

    try:
        with open('config/config.conf'):
            # TO DO: do stuffs with the config files
            pass
    except:
        QMessageBox.warning(None, "Error", "Couldn't open config file")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    session = session.Session()
    main_window = main_window.MainWindow(760, 520, app.desktop(), session)
    main_window.show()

    sys.exit(app.exec_())
