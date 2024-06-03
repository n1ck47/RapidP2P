from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature

class Peer:
    def __init__(self, env, bandwidth):
        self.env = env
        self.bandwidth = bandwidth
        self.id = None
        self.pub_key = None
        self.prv_key = None

    def gen_key_pair(self):
        private_value = 0x63bd3b01c5ce749d87f5f7481232a93540acdb0f7b5c014ecd9cd32b041d6f33
        curve = ec.SECP256R1()

        self.prv_key = ec.derive_private_key(private_value, curve, default_backend())
        self.pub_key = self.prv_key.public_key()

    def sign(self, data):
        signature_algorithm = ec.ECDSA(hashes.SHA256())
        return self.prv_key.sign(data.encode('utf-8'), signature_algorithm)
    
    def verify_sign(self, data, signature):
        signature_algorithm = ec.ECDSA(hashes.SHA256())
        try:
            self.pub_key.verify(signature, data.encode('utf-8'), signature_algorithm)
            print('Verification OK')
        except InvalidSignature:
            print('Verification failed')

    def get_id(self):
        pass


    
