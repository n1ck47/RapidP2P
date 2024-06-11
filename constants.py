from gas_fees import get_gas_fees 

R_MAX = 10**2 # in gwei
EPOCH_TIME = 0.1 # in seconds
MSSG_SIZE = 1024 # in Kb
N = 100 # no of nodes
COMM_SIZE = 10 # expected committe size of the aggregators
BALANCE = 10**9 # in gwei, starting balance of each node
INTER_TIME = 0.5 # in secs, expected inter arrival time between sending mssgs
SIMULATION_TIME = 1 # in secs
MIN_BANDWIDTH = 0.1 # in Mb
MAX_BANDWIDTH = 300 # in Mb
API_KEY = '7JDC8S1TS4QCWWJ8P7TTR6U7UGBFFFH9R1'

# R_MAX = int(get_gas_fees(API_KEY)['ProposeGasPrice']) / (10 ** 1)