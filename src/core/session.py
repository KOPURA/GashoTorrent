import libtorrent as lt
from core.alert_dispatcher import AlertDispatcher
from core.torrent_info_getter import InfoGetter


class Session(lt.session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.isAlive = True

        self.__dispatch_alerts()
        self.InfoGetter = InfoGetter

        # self.listen_on(# get from conf, #get from con)

    def destruct_session(self):
        self.isAlive = False

    def add_torrent(self, name):
        pass

    # Make additional thread to read alerts
    def __dispatch_alerts(self):
        dispatch = AlertDispatcher(self)
        dispatch.start()

# TO DO: Add some represenation of the torrents queue