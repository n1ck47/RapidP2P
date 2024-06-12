import csv
import matplotlib.pyplot as plt
from constants import SIMULATION_TIME, N

# Function to read data from CSV file
def read_data_from_csv(file_path):
    bandwidth = []
    reward = []
    txn_cost = [0,0]
    gas_cost = []
    profit = []
    slow_count = 0
    reward_tot = [0,0] # slow, fast
    for i in range (1, 11):
        file_path = f'./output/0.3/{i}.csv'

        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                bandwidth.append(int(row['SLOW?']))
                reward.append(float(row['Reward Earned']))
                if(int(row['SLOW?'])):
                    slow_count+=1
                    reward_tot[0] += float(row['Reward Earned'])
                    txn_cost[0] += float(row['Reward Cost'])
                else:
                    reward_tot[1] += float(row['Reward Earned'])
                    txn_cost[1] += float(row['Reward Cost'])

                gas_cost.append(float(row['Gas Cost']))
                profit.append(reward[-1] - gas_cost[-1])
    fast_count = 10*N - slow_count
    reward_avg = [reward_tot[0]/slow_count, reward_tot[1]/fast_count]
    txn_cost_avg = [txn_cost[0]/slow_count, txn_cost[1]/fast_count]
    profit_avg = [reward_tot[0]/slow_count-txn_cost[0]/slow_count, reward_tot[1]/slow_count-txn_cost[1]/slow_count]
    print(slow_count, fast_count,reward_avg, txn_cost_avg, profit_avg)
    return bandwidth, reward

# Function to plot bar graph
def plot_bar_graph(bandwidth, reward):
    plt.bar(bandwidth, reward, color='skyblue')
    plt.xlabel('SLOW?')
    plt.ylabel('Reward')
    plt.title('Bandwidth vs Reward')
    plt.show()

# CSV file path
file_path = './output/12_06_2024_22_12_01.csv'

# Read data from CSV
bandwidth, reward = read_data_from_csv(file_path)

# Plot bar graph
# plot_bar_graph(bandwidth, reward)
