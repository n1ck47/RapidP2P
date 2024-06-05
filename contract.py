import vrf
from constants import COMM_SIZE
from constants import N
from constants import BALANCE

class Contract:
    def __init__(self):
        self.last_id = 0
        self.mapping = list()
        self.mapping_hash = dict()
        self.randao = 0
        self.balances = list()
        self.locked_stakes = list()

    def assign_id(self, pub_key):
        if(pub_key in mapping_hash):
            return mapping_hash[pub_key]
        last_id += 1
        mapping.append(pub_key)
        balances.append(BALANCE)
        locked_stakes.append(0)
        mapping_hash[pub_key] = last_id
        return last_id

    def get_id(self, pub_key):
        return mapping_hash[pub_key]
    
    def lock_stakes(self, id, amount):
        if(id <= len(self.balances)):
            return False
        
        self.locked_stakes[id] += amount
        self.balances[id] -= amount
        return True
    
    def unlock_stakes(self):
        for i in range(len(self.balances)):
            amount = self.locked_stakes[i] 
            self.locked_stakes[i] = 0
            self.balances[i] += amount
    
    def get_balance(self, id):
        if(id >= len(self.balances)):
            return 0
        
        return balances[id]
    
    def verify_sortition(self, vrf_hash, proof, pub_key):
        seed = bytes(self.randao)
        is_valid = vrf.verify_vrf_proof(pub_key, seed, vrf_hash, proof)
        if not is_valid:
            return False

        probability = float(COMM_SIZE)/N
        hash_int = int.from_bytes(vrf_hash, byteorder='big')
        
        is_selected = ((hash_int / float(2**256)) <= probability)
        return is_selected

    def get_primary_agg(self, aggregators_proof):
        primary_agg = aggregators_proof[0]
        for agg in aggregators_proof:
            pub_key = agg.id
            is_valid = self.verify_sortition(agg.vrf_hash, agg.proof, pub_key)
            if not is_valid:
                continue
            
            agg_hash_int = int.from_bytes(vrf_hash, byteorder='big')
            p_agg_hash_int = int.from_bytes(primary_agg.vrf_hash, byteorder='big')
            if(agg_hash_int < p_agg_hash_int):
                primary_agg = agg

    def distribute_rewards(self):
        pass
