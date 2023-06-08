import sys
import os
import time
import pandas as pd


# Get the absolute path of the current script
script_path = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory of the script to the system path
parent_dir = os.path.abspath(os.path.join(script_path, ".."))
sys.path.append(parent_dir)

# Add the src module directory to the system path
src_dir = os.path.join(parent_dir, "src")
sys.path.append(src_dir)

from src import SpaceEfficientVQF


folder = "./data/biprimes/"
maxpow = 40

df = pd.read_csv(f"{folder}biprimes_maxpow_{maxpow}_number_200.csv")

biprimes = df["m=p*q"].to_list()

runtimes_folder = "./data/runtimes/"

# Define the path to the CSV file
csv_file = os.path.join(runtimes_folder, f"runtime_for_maxpow_{maxpow}.csv")

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
    time_taken = round(time_taken/60, 6)
    print(f'Time taken: {time_taken} min')
    print('')
    # Write number of bits and time taken to the CSV file
    data = {
        "m": [m],
        "Number of Bits": [number_of_bits],
        "Time Taken": [time_taken]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_file, mode="a", header=not os.path.exists(csv_file), index=False)
