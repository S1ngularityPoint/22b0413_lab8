import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import sem, t
import numpy as np
import os

# Configuration for experiments
tcp_variants = ["reno", "cubic"]
delays = [10, 50, 100]  # ms
losses = [0.1, 0.5, 1.0]  # percentage
confidence_level = 0.90

def load_data(variant, delay, loss):
    """Load throughput data for a given TCP variant, delay, and loss from CSV files with raw values only."""
    filename = f"results_{variant}{delay}{loss}.csv"
    if os.path.exists(filename):
        # Load the file as a list of raw throughput values
        data = pd.read_csv(filename, header=None, names=["throughput"])
        data["throughput"] = data["throughput"].str.replace("Mbits/sec", "", regex=False).astype(float)
        #data["throughput"] = pd.to_numeric(data["throughput"], errors='coerce')
        print(data)
        return data["throughput"].dropna()  # Drop any NaN values
    else:
        print(f"Warning: {filename} not found.")
        return pd.Series([])


def calculate_confidence_interval(data):
    """Calculate the mean and 90% confidence interval for a series of data."""
    mean = np.mean(data)
    error_margin = sem(data) * t.ppf((1 + confidence_level) / 2, len(data) - 1)
    return mean, error_margin

def plot_throughput_vs_delay():
    """Plot Throughput vs. Delay for each Loss level, with separate lines for each TCP variant."""
    for loss in losses:
        plt.figure()
        for variant in tcp_variants:
            means = []
            error_margins = []
            for delay in delays:
                data = load_data(variant, delay, loss)
                mean, error_margin = calculate_confidence_interval(data)
                means.append(mean)
                error_margins.append(error_margin)
            # Plot with error bars
            plt.errorbar(delays, means, yerr=error_margins, label=f"{variant.capitalize()}", capsize=5)
        
        plt.title(f"Throughput vs. Delay (Loss={loss}%)")
        plt.xlabel("Delay (ms)")
        plt.ylabel("Throughput (Mbps)")
        plt.legend()
        plt.grid()
        plt.show()

def plot_throughput_vs_loss():
    """Plot Throughput vs. Loss for each Delay level, with separate lines for each TCP variant."""
    for delay in delays:
        plt.figure()
        for variant in tcp_variants:
            means = []
            error_margins = []
            for loss in losses:
                data = load_data(variant, delay, loss)
                print(data)
                mean, error_margin = calculate_confidence_interval(data)
                means.append(mean)
                error_margins.append(error_margin)
            # Plot with error bars
            plt.errorbar(losses, means, yerr=error_margins, label=f"{variant.capitalize()}", capsize=5)
        
        plt.title(f"Throughput vs. Loss (Delay={delay}ms)")
        plt.xlabel("Loss (%)")
        plt.ylabel("Throughput (Mbps)")
        plt.legend()
        plt.grid()
        plt.show()

# Generate plots
plot_throughput_vs_delay()
plot_throughput_vs_loss()
