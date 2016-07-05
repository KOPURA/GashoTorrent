from PyQt5.Qt import QApplication
from PyQt5.QtWidgets import QMessageBox
from ui.main_window import MainWindow
from core.session import Session
from core.util import Utility
import sys
import logging


CONFIG_FILE_PATH = "config/config.conf"


if __name__ == '__main__':
    app = QApplication(sys.argv)
    logging.basicConfig(level=logging.INFO)

    try:
        session = Session(CONFIG_FILE_PATH)
    except ValueError as e:
        QMessageBox.warning(None, "Error", "Error parsing config file...")
        sys.exit(1)
    except (OSError, IOError) as e:
        QMessageBox.warning(None, "Error", "Couldn't open config file")
        sys.exit(1)

    main_window = MainWindow(app.desktop(), session)
    main_window.show()

    sys.exit(app.exec_())
