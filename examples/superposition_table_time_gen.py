import sys
import os
import time
import pandas as pd
import numpy as np

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

# Define the path to the text file
text_file = os.path.join(runtimes_folder, f"tables_stats_maxpower_{maxpow}.txt")

# Create a text file for writing logs
with open(text_file, "w") as f:
    # Iterate over the biprimes
    for m in biprimes:
        print(f"\t\tConsidering biprime: {m}")
        print("")
        # Write to the text file
        f.write(f"\t\tConsidering biprime: {m}\n\n")

        # Measure the time taken for executing superposition_tables
        start_time = time.time()

        vqf = SpaceEfficientVQF(m)
        known_bits = vqf.known_bits
        print(known_bits)
        print("")
        f.write(f"Known Bits: {known_bits}\n\n")

        for index, (c, table) in enumerate(vqf.table_clause_dict.items()):
            print(f"Superposition Table: {index+1}")
            print("------------------------")
            print(f"Clause: {c.clause}")
            n_vars = len(table.bits)
            n_rows = len(table.table)
            r_val = table.calc_r()

            print(f"Number of Variables: {n_vars}")
            print(f"Number of Rows: {n_rows} (log: {np.round(np.log2(n_rows), 5)})")
            print(f"R Value: {np.round(r_val, 5)}")
            print("================================================================")

            # Write to the text file
            f.write(f"Superposition Table: {index+1}\n")
            f.write("------------------------\n")
            f.write(f"Clause: {c.clause}\n")
            f.write(f"Number of Variables: {n_vars}\n")
            f.write(f"Number of Rows: {n_rows} (log: {np.round(np.log2(n_rows), 5)})\n")
            f.write(f"R Value: {np.round(r_val, 5)}\n")
            f.write(
                "================================================================\n"
            )

        end_time = time.time()
        time_taken = end_time - start_time
        time_taken = round(time_taken / 60, 6)
        print(f"Time taken: {time_taken} min")
        print("")
        f.write(f"Time taken: {time_taken} min\n\n")
