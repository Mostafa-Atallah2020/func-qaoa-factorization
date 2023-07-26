import sys
import os
import time
import pandas as pd
import numpy as np
import csv
from tqdm import tqdm

# Get the absolute path of the current script
script_path = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory of the script to the system path
parent_dir = os.path.abspath(os.path.join(script_path, ".."))
sys.path.append(parent_dir)

# Add the src module directory to the system path
src_dir = os.path.join(parent_dir, "src")
sys.path.append(src_dir)

# Load data from CSV
folder = "./data/biprimes/"
maxpow = 10  # 40

# Import custom modules (Replace 'SpaceEfficientVQF' and 'get_key_by_value' with actual implementation)
from src import SpaceEfficientVQF
from src.clause_utils import get_key_by_value

df = pd.read_csv(f"{folder}biprimes_maxpow_{maxpow}_number_200.csv")

biprimes = df["m=p*q"].to_list()

# Create results folder if it doesn't exist
results_folder = "./data/results/"
if not os.path.exists(results_folder):
    os.makedirs(results_folder)

# Create a CSV file for real-time data saving
output_file = os.path.join(results_folder, f"biprime_comp_ratio_maxpow_{maxpow}.csv")

# Initialize the CSV file and write the header
with open(output_file, "w", newline="") as csvfile:
    fieldnames = ["m", "total_var", "n_known_bits", *["r_" + str(i+1) for i in range(2)], "compression_ratio", "time_taken"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

# Begin the main loop with tqdm progress bar
start_time_program = time.time()
for m in tqdm(biprimes, desc="Processing biprimes", unit=" biprime"):

    vqf = SpaceEfficientVQF(m)

    total_var = len(vqf.p_bits) + len(vqf.q_bits)
    n_known_bits = len(vqf.known_bits)

    r_vals = []
    for t in vqf.superposition_tables:
        r = np.abs(t.calc_r())
        r_vals.append(r)

    compression_ratio = sum(r_vals) + n_known_bits

    # Calculate the time taken for each m
    start_time_m = time.time()

    # Calculate compression ratio and save data to CSV
    with open(output_file, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        row_data = {
            "m": m,
            "total_var": total_var,
            "n_known_bits": n_known_bits,
            **{"r_" + str(i+1): r for i, r in enumerate(r_vals)},
            "compression_ratio": compression_ratio,
            "time_taken": time.time() - start_time_m
        }

        writer.writerow(row_data)

    # Print data to the screen
    #print(f"m: {m}, total_var: {total_var}, n_known_bits: {n_known_bits}, compression_ratio: {compression_ratio}, time_taken: {row_data['time_taken']:.2f} seconds")

# Calculate total time since the beginning of the program
total_time = time.time() - start_time_program
print(f"Total time elapsed: {total_time:.2f} seconds")
