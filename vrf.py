from ecdsa import SigningKey, VerifyingKey
import hashlib

def generate_vrf_proof(sk: SigningKey, message: bytes):
    proof = sk.sign_deterministic(message, hashfunc=hashlib.sha256)

    vrf_hash = hashlib.sha256(proof).digest()
    return vrf_hash, proof

def verify_vrf_proof(vk: VerifyingKey, message: bytes, vrf_hash: bytes, proof: bytes):
    try:
        vk.verify(proof, message, hashfunc=hashlib.sha256)
        computed_hash = hashlib.sha256(proof).digest()
        return computed_hash == vrf_hash
    except BadSignatureError:
        return False
