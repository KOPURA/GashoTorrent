from threading import Thread
import logging


class AlertDispatcher(Thread):
    def __init__(self, session):
        super().__init__()

        self.session = session
    
    def run(self):
        while self.session.isAlive:
            self.session.wait_for_alert(500)
            alert = self.session.pop_alert()
            if not alert:
                continue

            logging.info(("[{}]: {}").format(type(alert), alert.__str__()))
