from constants import MSSG_SIZE

import uuid

class Message:
    def __init__(self, data, peer_id, epoch):
        self.uuid = uuid.uuid4()
        self.data = data
        self.size = MSSG_SIZE
        self.peer_id = peer_id
        self.epoch = epoch

class Bundle:
    def __init__(self, mssg):
        self.mssg = mssg
        self.ids = list()

    def tag_id(self, id):
        self.ids.append(id)