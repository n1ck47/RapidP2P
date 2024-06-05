import simpy
from constants import N
# from network import intialize_network
from contract import Contract
from peer import Peer

def main(n):
    env = simpy.Environment()
    sc = Contract()
    p1 = Peer(1,1)
    p1.gen_key_pair()
    (vrf_hash, proof, is_selected) = p1.sortition(sc)
    print(p1.verify_sortition(vrf_hash, proof, sc))
    # mssg = "as".encode('utf-8')
    # create nodes


    # setup network
    # network = intialize_network(n) 
    




if __name__ == "__main__":
    main(N)