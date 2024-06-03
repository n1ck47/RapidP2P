import simpy
from constants import N
from network import intialize_network

def main(n):
    env = simpy.Environment()
    network = intialize_network(n) 
    




if __name__ == "__main__":
    main(N)