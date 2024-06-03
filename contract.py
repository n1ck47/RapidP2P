class Contract:
    def __init__(self):
        last_id = 0
        mapping = list()

    def assign_id(self, pub_key):
        last_id += 1
        mapping.append(pub_key)
        return last_id
    
    def get_primary_agg(self):
        pass

    def distribute_rewards(self):
        pass