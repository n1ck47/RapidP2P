class Message:
    def __init__(self, data):
        self.data = data

class Bundle:
    def __init__(self, mssg, peer):
        self.mssg = mssg
        self.ids = [peer.id]

    def tag_id(self, peer):
        self.ids.append(peer.id)