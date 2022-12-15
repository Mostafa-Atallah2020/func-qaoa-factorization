"""
Generate circuit parameters for QAOA of vqf algorithm.
"""
import csv
from time import time

import pandas as pd
from qiskit import Aer, transpile
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit.utils import algorithm_globals
from vqf import get_cost_hamiltonian

algorithm_globals.random_seed = 10598
optimizer = COBYLA()
instance = Aer.get_backend("aer_simulator")
qaoa = QAOA(optimizer, quantum_instance=instance)

if __name__ == "__main__":

    number_of_biprimes = 200
    max_pow = 40
    biprimes = []
    file_in = f"./final_data_biprimes/biprimes_maxpow_{max_pow}_number_{number_of_biprimes}.csv"

    file_out = {}
    circ_params = {}
    for level in range(4):
        file_out[
            level
        ] = f"./qaoa_data/qaoa_circ_params_max_power_{max_pow}_transpile_level_{level}.csv"
        circ_params[level] = []

    df = pd.read_csv(file_in)
    biprimes = list(df["m=p*q"].values)

    t = time()
    for m in biprimes:

        print(f"Considering biprime: {m} \n")
        H = get_cost_hamiltonian(m)

        params = [
            1,
            1,
        ]  # a typical QAOA ansatz has two parameters, we set them to be ones.
        qc = qaoa.construct_circuit(params, H)
        qc = qc[0]

        for level in range(4):
            print(f"Optimization Level {level}")
            t_circ = transpile(qc, basis_gates=["cx", "u3"], optimization_level=level)
            n_qubits = t_circ.num_qubits
            depth = t_circ.depth()
            gates = t_circ.count_ops()
            n_cnots = gates["cx"]
            n_u3 = gates["u3"]
            n_gates = n_cnots + n_u3

            result = [m, n_qubits, depth, n_gates, n_cnots, n_u3]
            print("results: ")
            print(result)
            print(f"Computation finished ({round((time()-t)/60, 3)} min) \n")
            circ_params[level].append(result)

    for level in range(4):
        with open(file_out[level], "w") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(
                ["biprime", "n_qubits", "depth", "n_gates", "n_cnot", "n_u3"]
            )
            csvwriter.writerows(circ_params[level])
