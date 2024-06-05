from ecdsa import SigningKey, SECP256k1

from constants import COMM_SIZE
from constants import N
import vrf

class Peer:
    def __init__(self, env, bandwidth):
        self.env = env
        self.bandwidth = bandwidth
        self.id = None
        self.pub_key = None
        self.prv_key = None

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


    
