from PyQt5.QtCore import QThread, pyqtSignal
import time
import logging


class DataConsumer(QThread):
    dataReceived = pyqtSignal(dict)

    def __init__(self, parent, session, timeout=2, wait_on_tick=0.2):
        super().__init__(parent)

        self.session = session
        self.timeout = timeout
        self.wait_on_tick = wait_on_tick

    def run(self):
        while self.session.is_alive():
            if self.session.data_queue.empty():
                time.sleep(self.timeout)
                continue

            rowData = self.session.data_queue.pop()
            self.dataReceived.emit(rowData)

            time.sleep(self.wait_on_tick)

        logging.info("Exiting the data consumer...")
