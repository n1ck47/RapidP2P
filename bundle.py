from constants import MSSG_SIZE, MIN_MSG_SIZE, MAX_MSG_SIZE

import uuid
import numpy as np

class Message:
    def __init__(self, data, peer_id, epoch):
        self.uuid = uuid.uuid4()
        self.data = data
        self.size = np.random.uniform(MIN_MSG_SIZE, MAX_MSG_SIZE)
        self.peer_id = peer_id
        self.epoch = epoch

class Bundle:
    def __init__(self, mssg):
        self.mssg = mssg
        self.ids = list()

    def tag_id(self, id):
        self.ids.append(id)