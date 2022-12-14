from utils import construct_and_get_info_of_QAOA_modulo_layer_circuit, get_gates
import csv
import numpy as np

if __name__ == "__main__":


    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--maxpow", type=int, default=10, required=False)
    parser.add_argument("-n", "--number", type=int, default=100, required=False)
    parser.add_argument("-l", "--levels", type=int, default=1,required=False)
    parser.add_argument("--dirin", type=str, default="final_data_biprimes")
    parser.add_argument("--dirout", type=str, default="plot_data")
    

    args = parser.parse_args()


    number_of_biprimes = args.number
    max_pow = args.maxpow
    lvl = args.levels
    filename = f"../../Mostafa and Ludmilla/{args.dirin}/biprimes_maxpow_{max_pow}_number_{number_of_biprimes}.csv"
    # filename = f"./{args.dirin}/biprimes_maxpow{max_pow}_number{number_of_biprimes}.csv"
    
    biprimes = []

    with open(filename, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)
        for row in csvreader:
            int_row = [int(i) for i in row]
            biprimes.append(int_row)

    data = np.asarray(biprimes)[:,-1]

    num_qubits, num_clbits, depths, num_gates, n = construct_and_get_info_of_QAOA_modulo_layer_circuit(data, lvl = lvl)
    cx_gates, u3_gates = get_gates(num_gates)

    