import csv
import matplotlib.pyplot as plt
from constants import SIMULATION_TIME, N
import pandas as pd
import numpy as np
from scipy.stats import norm, t

def calculate_confidence_interval(data, confidence=0.95):
    n = len(data)
    mean = np.mean(data)
    std_dev = np.std(data, ddof=1)  # ddof=1 to get the sample standard deviation
    se = std_dev / np.sqrt(n)
    # z_score = norm.ppf((1 + confidence) / 2)
    t_score = t.ppf((1 + confidence) / 2, df=n-1)
    margin_of_error = t_score * se
    confidence_interval = (mean - margin_of_error, mean + margin_of_error)
    
    return mean, confidence_interval

def calc_conf():
    
    slow_means = list()
    slow_ci_lower = list()
    slow_ci_upper = list()
    fast_means = list()
    fast_ci_lower = list()
    fast_ci_upper = list()
    for sf in range(1, 10, 2):
        slow_frac = sf/10
        no_of_files = 10
        if(slow_frac==0.1):
            no_of_files = 9
        slow_reward, fast_reward = list(), list()
        for i in range (1, no_of_files+1):
            slow_count = 0
            reward_tot = [0,0] # slow, fast
            file_path = f'./output/slow_vs_fast/{slow_frac}/{i}.csv'

            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if(int(row['SLOW?'])):
                        slow_count+=1
                        reward_tot[0] += float(row['Reward Earned'])
                    else:
                        reward_tot[1] += float(row['Reward Earned'])

            fast_count = N - slow_count
            slow_reward.append(reward_tot[0]/slow_count)
            fast_reward.append(reward_tot[1]/fast_count)
        
        
        mean, ci = calculate_confidence_interval(slow_reward)
        slow_means.append(mean)
        slow_ci_lower.append(ci[0])
        slow_ci_upper.append(ci[1])
        mean, ci = calculate_confidence_interval(fast_reward)
        fast_means.append(mean)
        fast_ci_lower.append(ci[0])
        fast_ci_upper.append(ci[1])

    # Plotting
    plt.figure(figsize=(12, 6))
    x_positions = np.arange(5)

    # Plot the mean and confidence intervals
    plt.errorbar(x_positions, slow_means, yerr=[np.array(slow_means) - np.array(slow_ci_lower), np.array(slow_ci_upper) - np.array(slow_means)], fmt='o', capsize=5, label='Slow peers')
    plt.errorbar(x_positions, fast_means, yerr=[np.array(fast_means) - np.array(fast_ci_lower), np.array(fast_ci_upper) - np.array(fast_means)], fmt='o', capsize=5, label='Fast peers')

    # Add labels and title
    plt.xlabel('Percentage of slow peers')
    plt.ylabel('Reward earned')
    plt.title('95% Confidence Intervals for slow and fast peers at different fraction of slow peers ')
    plt.xticks(x_positions, [f'{(i+1)*2*10 - 10}' for i in x_positions])
    plt.legend()

    # Save the plot as an image file
    plt.savefig('confidence_intervals.png')

    # Close the plot to free up memory
    plt.close()
    

# Function to read data from CSV file
def read_data_from_csv(file_path):
    bandwidth = []
    reward = []
    txn_cost = [0,0]
    gas_cost = []
    profit = []
    slow_count = 0
    reward_tot = [0,0] # slow, fast
    no_of_files = 9
    for i in range (1, no_of_files+1):
        file_path = f'./output/slow_vs_fast/0.9/{i}.csv'

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
    fast_count = N*no_of_files - slow_count
    reward_avg = [reward_tot[0]/slow_count, reward_tot[1]/fast_count]
    txn_cost_avg = [txn_cost[0]/slow_count, txn_cost[1]/fast_count]
    profit_avg = [reward_avg[0]-txn_cost_avg[0], reward_avg[1]-txn_cost_avg[1]]
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
# file_path = './output/14_06_2024_11_08_29.csv'

# Read data from CSV
# bandwidth, reward = read_data_from_csv(file_path)
calc_conf()
