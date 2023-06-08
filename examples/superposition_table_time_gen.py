import sys
import os
import csv
import time


# Get the absolute path of the current script
script_path = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory of the script to the system path
parent_dir = os.path.abspath(os.path.join(script_path, ".."))
sys.path.append(parent_dir)

# Add the src module directory to the system path
src_dir = os.path.join(parent_dir, "src")
sys.path.append(src_dir)

import pandas as pd
from src import SpaceEfficientVQF


folder = "./data/biprimes/"
maxpow = 10

df = pd.read_csv(f"{folder}biprimes_maxpow_{maxpow}_number_200.csv")

biprimes = df["m=p*q"].to_list()
biprimes = biprimes[:3]

runtimes_folder = "./data/runtimes/"

# Define the path to the CSV file
csv_file = os.path.join(runtimes_folder, "time_taken.csv")

# Open the CSV file in append mode
with open(csv_file, mode="a", newline="") as file:
    writer = csv.writer(file)

    # Iterate over the biprimes
    for m in biprimes:
        print(f'Considering biprime: {m}')
        # Measure the time taken for executing superposition_tables
        start_time = time.time()
        number_of_bits = len(bin(m)[2:])
        vqf = SpaceEfficientVQF(m)
        superposition_tables = vqf.superposition_tables
        end_time = time.time()
        time_taken = end_time - start_time
        print(f'Time taken: {time_taken} seconds')

        # Write number of bits and time taken to the CSV file
        writer.writerow([m, number_of_bits, time_taken])
