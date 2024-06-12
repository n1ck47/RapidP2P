from gas_fees import get_gas_fees 

R_MAX = 10**2 # in gwei
EPOCH_TIME = 2 # in seconds
MSSG_SIZE = 10*3 # in Kb
N = 100 # no of nodes
COMM_SIZE = 10 # expected committe size of the aggregators
BALANCE = 10**9 # in gwei, starting balance of each node
INTER_TIME = 0.5 # in secs, expected inter arrival time between sending mssgs
SIMULATION_TIME = 60 # in secs
MIN_BANDWIDTH = 1 # in Mb
MAX_BANDWIDTH = 300 # in Mb
API_KEY = '7JDC8S1TS4QCWWJ8P7TTR6U7UGBFFFH9R1'
MIN_LINKS = 4
MAX_LINKS = 8
SLOW_BANDWIDTH = 1 # in Mb
FAST_BANDWIDTH = 100 # in Mb
SLOW_PEERS = 0.3 # fraction of slow peers in the network

# R_MAX = int(get_gas_fees(API_KEY)['ProposeGasPrice']) / (10 ** 1)