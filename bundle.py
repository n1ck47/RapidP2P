from constants import MSSG_SIZE

class Message:
    def __init__(self, data, peer_id):
        self.data = data
        self.size = MSSG_SIZE
        self.peer_id = peer_id

class Bundle:
    def __init__(self, mssg):
        self.mssg = mssg
        self.ids = list()

    def tag_id(self, peer):
        self.ids.append(peer.id)