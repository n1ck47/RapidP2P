from ecdsa import SigningKey, SECP256k1
import copy

from constants import COMM_SIZE, N, R_MAX, INTER_TIME
from bundles import Message, Bundle
import vrf

class Peer:
    network = None

    def __init__(self, env, bandwidth):
        self.env = env
        self.bandwidth = bandwidth
        self.id = None
        self.pub_key = None
        self.prv_key = None
        self.neighbours = list()
        self.mssg_pool = dict()
        self.is_gen_mssg = False
        self.link_speed = 0 # set link random speed

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

    def register(self, sc):
        self.id = sc.assign_id(self.pub_key)
    
    def get_id(self, sc):
        self.id = sc.get_id(self.pub_key)
        return self.id

    def sortition(self, sc):
        seed = bytes(sc.randao)
        vrf_hash, proof = vrf.generate_vrf_proof(self.prv_key, seed)
        probability = float(COMM_SIZE)/N
        hash_int = int.from_bytes(vrf_hash, byteorder='big')
        
        is_selected = ((hash_int / float(2**256)) <= probability)
        return (vrf_hash, proof, is_selected)
        
    def verify_sortition(self, vrf_hash, proof, pub_key):
         seed = bytes(sc.randao)
         return vrf.verify_vrf_proof(pub_key, seed, vrf_hash, proof)

    # compute latency b/w self and receiver link
    def compute_delay(self, bundle, receiver):  
        link_speed = min(self.link_speed, receiver.link_speed)
        mssg_size = bundle.mssg.size
        latency = None # add latency
        return latency

    def generate_mssg(self, sc):
        while True:
            balance = sc.get_balance(self.id)
            if balance < R_MAX: 
                break

            sc.lock_stakes(R_MAX)

            mssg = Message("heya")
            bundle = Bundle(mssg, self.id)
            new_bundle = copy.deepcopy(bundle)
            new_bundle.tag_id((self.id))

            self.mssg_pool[mssg] = bundle
            delay = np.random.exponential(INTER_TIME) 

            self.env.process(self.broadcast_bundle(None, new_bundle)) 
            yield self.env.timeout(delay)
            
        self.is_gen_mssg = False 
    
    def broadcast_bundle(self, prev_node, bundle):
        mssg_events = list()
        for node_id in self.neighbours:
            if prev_node == node_id: 
                continue

            receiver = self.network[node_id]
            event = self.env.process(self.send_bundle(bundle, receiver))
            mssg_events.append(event)

        yield self.env.all_of(mssg_events)

    def send_bundle(self, bundle, receiver):
        delay = self.compute_delay(bundle, receiver) 
        yield self.env.timeout(delay)   
        self.env.process(receiver.recv_bundle(self, bundle))

    def recv_bundle(self, sender, bundle):
        if bundle.mssg in self.mssg_pool: 
            bundle_length = len(bundle.ids)
            older_bundle = self.mssg_pool[bundle.mssg]
            older_bundle_length = len(older_bundle.ids)
            if(older_bundle_length <= bundle_length):
                return

        self.mssg_pool[bundle.mssg] = bundle
        new_bundle = copy.deepcopy(bundle)
        new_bundle.tag_id(self.id)

        yield self.env.process(self.broadcast_bundle(sender, new_bundle)) 

