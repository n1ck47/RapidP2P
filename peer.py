from ecdsa import SigningKey, SECP256k1
import numpy as np
import random
import copy
from pprint import pprint
import hashlib

from constants import COMM_SIZE, N, R_MAX, INTER_TIME, EPOCH_TIME, MIN_BANDWIDTH, MAX_BANDWIDTH
from bundle import Message, Bundle
import vrf

class Peer:
    network = None
    contract = None

    def __init__(self, env):
        self.env = env
        self.bandwidth = np.random.uniform(MIN_BANDWIDTH, MAX_BANDWIDTH) # in Mbps
        self.id = None
        self.pub_key = None
        self.prv_key = None
        self.neighbours = list() 
        self.bundle_pool = dict()
        self.mssg_pool = dict() # epoch to mssg list
        self.is_gen_mssg = False

    def reset(self, env):
        self.env = env
        self.bundle_pool.clear()
        self.mssg_pool.clear()
        self.is_gen_mssg = False

    def gen_key_pair(self):
        self.prv_key = SigningKey.generate(curve=SECP256k1)
        self.pub_key = self.prv_key.get_verifying_key()

    def sign(self, message):
        return self.prv_key.sign(message)
    
    def verify_sign(self, message, signature):
        try:
            self.pub_key.verify(signature, message)
            return True
        except:
            return False

    def register(self):
        self.id = self.contract.assign_id(self.pub_key)
    
    def get_id(self):
        self.id = self.contract.get_id(self.pub_key)
        return self.id
    
    def get_epoch(self):
        current_time = self.env.now
        return current_time//EPOCH_TIME + 1

    def sortition(self):
        
        seed = bytes(self.contract.randao)
        vrf_hash, proof = vrf.generate_vrf_proof(self.prv_key, seed)
        probability = COMM_SIZE/N
        hash_int = int.from_bytes(vrf_hash, byteorder='big')
        
        is_selected = ((hash_int / float(2**256)) <= probability)
        # print(self.id, self.env.now, self.get_epoch(), hash_int / float(2**256), probability, is_selected)
        return (vrf_hash, proof, is_selected)
        
    def verify_sortition(self, vrf_hash, proof, pub_key):
         seed = bytes(self.contract.randao)
         return vrf.verify_vrf_proof(pub_key, seed, vrf_hash, proof)

    def aggregator_operation(self, vrf_hash, proof):
        yield self.env.timeout(EPOCH_TIME/2)
        epoch = self.get_epoch()
        if (epoch-1) in self.mssg_pool:
            mssgs = self.mssg_pool[epoch-1]
            res_bundles = list()

            for mssg in mssgs:
                bundle = self.bundle_pool[mssg]
                new_bundle = copy.deepcopy(bundle)
                new_bundle.tag_id(self.id)
                res_bundles.append(new_bundle)
            
            res_vrf = dict()
            res_vrf['vrf_hash'] = vrf_hash
            res_vrf['proof'] = proof
            res_vrf['id'] = self.id
            randao = bytes(self.contract.randao)
            signature = bytes(hashlib.sha256(self.prv_key.sign_deterministic(bytes(randao), hashfunc=hashlib.sha256)).digest())
            new_randao = bytes(a ^ b for a, b in zip(randao, signature))

            self.env.process(self.contract.submit_proof(res_bundles, res_vrf, new_randao))

    def run(self):
        while True:
            if(self.get_epoch() == 1):
                yield self.env.timeout(EPOCH_TIME)
                continue
            (vrf_hash, proof, is_selected) = self.sortition()
            if(is_selected):
                self.env.process(self.aggregator_operation(vrf_hash, proof))
                yield self.env.timeout(EPOCH_TIME)
            else:
                yield self.env.timeout(EPOCH_TIME)
            

    # compute latency b/w self and receiver link
    def compute_delay(self, bundle, receiver):  
        bandwidth = min(self.bandwidth, receiver.bandwidth)
        mssg_size = bundle.mssg.size
        # ρij = random.uniform(0.2, 0.25)
        # dij = np.random.exponential(scale= 96/(bandwidth*1000)) # 96Kbits
        # latency = ρij + (mssg_size / (bandwidth*1000)) + dij
        latency = (mssg_size / (bandwidth*1000))
        # print(ρij,(mssg_size / (bandwidth*1000)), dij)
        return latency

    def generate_mssg(self):
        while True:
            balance = self.contract.get_balance(self.id)
            if balance < R_MAX: 
                break

            self.contract.lock_stakes(self.id, R_MAX)

            epoch = self.get_epoch()
            mssg = Message("heya", self.id, epoch)
            bundle = Bundle(mssg)
            new_bundle = copy.deepcopy(bundle)
            new_bundle.tag_id((self.id))

            self.bundle_pool[mssg.uuid] = bundle
            if(epoch in self.mssg_pool):
                self.mssg_pool[epoch].append(mssg.uuid)
            else:
                self.mssg_pool[epoch] = [mssg.uuid]

            delay = np.random.exponential(INTER_TIME) 
            self.env.process(self.broadcast_bundle(None, new_bundle)) 
            yield self.env.timeout(delay)
            
        self.is_gen_mssg = False 
    
    def broadcast_bundle(self, prev_node, bundle):
        mssg_events = list()
        # print(prev_node)
        for node_id in self.neighbours:
            if prev_node == node_id: 
                continue

            receiver = self.network[node_id]
            event = self.env.process(self.send_bundle(bundle, receiver))
            mssg_events.append(event)

        yield self.env.all_of(mssg_events)

    def send_bundle(self, bundle, receiver):
        delay = self.compute_delay(bundle, receiver) 
        # print(delay)
        yield self.env.timeout(delay)   
        self.env.process(receiver.recv_bundle(self, bundle))

    def recv_bundle(self, sender, bundle):
        # print(sender)
        # print(bundle.ids, self.id, bundle.mssg)
        if bundle.mssg.uuid in self.bundle_pool: 
            # return 
            # print('g')
            bundle_length = len(bundle.ids)
            older_bundle = self.bundle_pool[bundle.mssg.uuid]
            older_bundle_length = len(older_bundle.ids)
            if(older_bundle_length <= bundle_length):
                # print('a')
                return
        else:
            epoch = bundle.mssg.epoch
            if(epoch in self.mssg_pool):
                self.mssg_pool[epoch].append(bundle.mssg.uuid)
            else:
                self.mssg_pool[epoch] = [bundle.mssg.uuid]

        self.bundle_pool[bundle.mssg.uuid] = bundle
        new_bundle = copy.deepcopy(bundle)
        new_bundle.tag_id(self.id)

        yield self.env.process(self.broadcast_bundle(sender, new_bundle)) 

