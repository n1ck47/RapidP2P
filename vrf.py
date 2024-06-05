from ecdsa import SigningKey, VerifyingKey
import hashlib

def generate_vrf_proof(sk: SigningKey, message: bytes):
    # Generate a signature as the proof
    proof = sk.sign_deterministic(message, hashfunc=hashlib.sha256)
    # Generate a VRF hash (pseudo-random output) by hashing the proof
    vrf_hash = hashlib.sha256(proof).digest()
    return vrf_hash, proof

# Verify VRF proof and hash
def verify_vrf_proof(vk: VerifyingKey, message: bytes, vrf_hash: bytes, proof: bytes):
    # Verify the proof using the verifying key and message
    try:
        vk.verify(proof, message, hashfunc=hashlib.sha256)
        computed_hash = hashlib.sha256(proof).digest()
        return computed_hash == vrf_hash
    except BadSignatureError:
        return False
