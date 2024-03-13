import sys
import argparse
import csv

import pandas as pd
from time import time
from numpy import log2

sys.path.append(f"./../../")

from src import FactoringHamiltonian

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--maxpow", type=int, default=40, required=False)
    parser.add_argument("-n", "--number", type=int, default=200, required=False)
    parser.add_argument("-r", "--replace", action="store_true")
    parser.add_argument("-d", "--dir", type=str, default="./data/biprimes")
    args = parser.parse_args()

    number_of_biprimes = args.number
    max_pow = args.maxpow

    biprimes = []
    file_in = f"./../biprimes/biprimes_maxpow_{max_pow}_number_{number_of_biprimes}.csv"

    df = pd.read_csv(file_in)
    biprimes = list(df["m=p*q"].values)

    file_out = (
        f"./../results/circuit_params_maxpow_{max_pow}_number_{number_of_biprimes}.csv"
    )

    with open(file_out, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "Biprime",
                "Number of Qubits",
                "Number of CNOTs"
            ]
        )  # Header row

        t = time()
        for m in biprimes:
            print(f"Considering biprime: {m}")
            H = FactoringHamiltonian(m).hamiltonian
            n_qubits = len(H.bits)
            n_cnots = H.n_cnots
            result = [m, n_qubits, n_cnots]
            print("Results:")
            print(result)
            writer.writerow(result)
            print(f"Computation finished ({round((time()-t)/60, 3)} min)")

    print(f"All computations finished. Results saved in {file_out}.")
