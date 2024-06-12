import vrf
from constants import COMM_SIZE, N, BALANCE, EPOCH_TIME, R_MAX, API_KEY
from gas_fees import get_gas_fees

import copy
import hashlib
from pprint import pprint
import random

class Contract:
    def __init__(self, env):
        self.last_id = -1
        self.mapping = []
        self.mapping_hash = dict()
        self.randao = bytes(hashlib.sha256('0'.encode('utf-8')).digest())
        self.balances = []
        self.current_locked_stakes = []
        self.old_locked_stakes = []
        self.reward_earned = []
        self.reward_cost = []
        self.env = env
        self.aggregators_proof = list()
        self.gas_cost = []
        self.gas = int(get_gas_fees(API_KEY)['ProposeGasPrice'])
        self.sortition = True
        self.primary = random.choice(list(range(N)))

    def reset(self, env):
        l = len(self.balances)
        self.env = env
        self.aggregators_proof.clear()
        for i in range(l):
            self.current_locked_stakes[i] = 0
            self.old_locked_stakes[i] = 0
            self.reward_earned[i] = 0
            self.reward_cost[i] = 0
            self.gas_cost[i] = 0

    def get_epoch(self):
        current_time = self.env.now
        return int(current_time//EPOCH_TIME + 1)

    def assign_id(self, pub_key):
        pub_key_str = str(pub_key)
        if(pub_key_str in self.mapping_hash):
            return self.mapping_hash[pub_key_str]
        self.last_id += 1
        self.mapping.append(pub_key)
        self.balances.append(BALANCE)
        self.current_locked_stakes.append(0)
        self.old_locked_stakes.append(0)
        self.reward_cost.append(0)
        self.gas_cost.append(0)
        self.reward_earned.append(0)
        self.mapping_hash[pub_key_str] = self.last_id
        # print(self.mapping_hash)
        return self.last_id

    def get_id(self, pub_key):
        pub_key = str(pub_key)
        return self.mapping_hash[pub_key]
    
    def lock_stakes(self, id, amount):
        if(id <= len(self.balances)):
            return False
        
        self.current_locked_stakes[id] += amount
        self.balances[id] -= amount
        return True
    
    def lock_helper(self):
        while True:
            self.old_locked_stakes = copy.deepcopy(self.current_locked_stakes)
            self.current_locked_stakes.clear()
            yield self.env.timeout(EPOCH_TIME)
    
    def unlock_stakes(self):
        for i in range(len(self.balances)):
            amount = self.old_locked_stakes[i] 
            self.old_locked_stakes[i] = 0
            self.balances[i] += amount
        # yield self.env.timeout(0)
    
    def get_balance(self, id):
        if(id >= len(self.balances)):
            return 0
        
        return self.balances[id]
    
    def verify_sortition(self, vrf_hash, proof, pub_key):
        seed = bytes(self.randao)
        # print('aa', seed == seeda)
        is_valid = vrf.verify_vrf_proof(pub_key, seed, vrf_hash, proof)
        # print(is_valid)
        if not is_valid:
            return False

        probability = float(COMM_SIZE)/N
        hash_int = int.from_bytes(vrf_hash, byteorder='big')
        
        is_selected = ((hash_int / float(2**256)) <= probability)
        return is_selected

    def submit_proof(self, agg_bundles, agg_proof, randao):
        # print('hello')
        self.balances[agg_proof['id']] -= self.gas
        self.gas_cost[agg_proof['id']] += self.gas
        self.aggregators_proof.append([agg_bundles, agg_proof, randao])
        # print(agg_proof['id'], self.env.now, len(self.aggregators_proof))
        yield self.env.timeout(0)

    def get_primary_agg(self):
        while True:
            # print('okie', len(self.aggregators_proof))
            if(self.get_epoch() == 1):
                yield self.env.timeout(3* EPOCH_TIME/4)
            if(len(self.aggregators_proof)!=0):
                primary_agg = self.aggregators_proof[0]
                for agg in self.aggregators_proof:
                    agg_proof = agg[1]
                    # print(agg_proof)
                    pub_key = self.mapping[agg_proof['id']]
                    # print(agg[4])
                    # print(self.mapping_hash)
                    # print('key', pub_key==agg[4], self.mapping_hash[str(agg[4])], agg_proof['id'])
                    is_valid = self.verify_sortition(agg_proof['vrf_hash'], agg_proof['proof'], pub_key)
                    # print(is_valid)
                    if(self.sortition and not is_valid):
                        continue
                    
                    agg_hash_int = int.from_bytes(agg_proof['vrf_hash'], byteorder='big')
                    p_agg_hash_int = int.from_bytes(primary_agg[1]['vrf_hash'], byteorder='big')
                    if(agg_hash_int < p_agg_hash_int):
                        primary_agg = agg

                print(f"Time: {self.env.now}, No of Aggr: {len(self.aggregators_proof)}")
                self.aggregators_proof.clear()
                self.randao = primary_agg[2]
                self.distribute_rewards(primary_agg)
            else:
                randao = bytes(self.randao)
                # print(self.get_epoch())
                epoch_hash = bytes(hashlib.sha256(bytes(self.get_epoch())).digest())
                new_randao = bytes(a ^ b for a, b in zip(randao, epoch_hash))
                # print('hei')
                self.randao = new_randao
            yield self.env.timeout(EPOCH_TIME)

    def distribute_rewards(self, primary_agg):
        # print(self.reward_earned)
        agg_id = primary_agg[1]['id']
        # print(self.env.now)
        bundles = primary_agg[0]
        # print(len(bundles), R_MAX)
        for bundle in bundles:
            l = len(bundle.ids)
            reward = R_MAX/(2**l)
            # print(l, reward)
            # pprint(vars(bundle))
            for id in bundle.ids:
                self.balances[id] += reward
                self.reward_earned[id] += reward
            
            # self.reward_earned[agg_id] -= reward
            mssg_originator = bundle.mssg.peer_id
            self.reward_cost[mssg_originator] += R_MAX
            self.old_locked_stakes[mssg_originator] -= R_MAX
        
        self.unlock_stakes() 

