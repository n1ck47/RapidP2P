import csv
import matplotlib.pyplot as plt
from constants import SIMULATION_TIME

# Function to read data from CSV file
def read_data_from_csv(file_path):
    bandwidth = []
    reward = []
    gas_cost = []
    profit = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            bandwidth.append(float(row['Bandwidth']))
            reward.append(float(row['Reward Earned']))
            gas_cost.append(float(row['Gas Cost']))
            profit.append(reward[-1] - gas_cost[-1])
    return bandwidth, reward

# Function to plot bar graph
def plot_bar_graph(bandwidth, reward):
    plt.bar(bandwidth, reward, color='skyblue')
    plt.xlabel('Bandwidth')
    plt.ylabel('Reward')
    plt.title('Bandwidth vs Reward')
    plt.show()

# CSV file path
file_path = './output/10_06_2024_20_02_57.csv'

# Read data from CSV
bandwidth, reward = read_data_from_csv(file_path)

# Plot bar graph
plot_bar_graph(bandwidth, reward)
