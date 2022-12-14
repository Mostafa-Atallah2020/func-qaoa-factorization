from utils import construct_and_get_info_of_QAOA_modulo_layer_circuit, get_gates
import csv
import numpy as np
# from joblib import Parallel, delayed


if __name__ == "__main__":

    from joblib import Parallel, delayed
    import pickle
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--maxpow", type=int, default=20, required=False)
    parser.add_argument("-n", "--number", type=int, default=100, required=False)
    parser.add_argument("-l", "--levels", type=int, default=1,required=False)
    parser.add_argument("--dirin", type=str, default="final_data_biprimes")
    parser.add_argument("--dirout", type=str, default="plot_data")
    

    args = parser.parse_args()


    number_of_biprimes = args.number
    max_pow = args.maxpow
    lvl = args.levels
    filename = f"../../Mostafa and Shamim/{args.dirin}/biprimes_maxpow{max_pow}_number{number_of_biprimes}.csv"
    # filename = f"./{args.dirin}/biprimes_maxpow{max_pow}_number{number_of_biprimes}.csv"
    
    biprimes = []

    with open(filename, "r") as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)
        for row in csvreader:
            int_row = [int(i) for i in row]
            biprimes.append(int_row)


    num_chunks = 10
    data = np.asarray(biprimes)[:,-1]
    results = Parallel(n_jobs=8)\
    (delayed(construct_and_get_info_of_QAOA_modulo_layer_circuit)([number],lvl=lvl) for number in data)

    with open(f"results/data_maxpow{max_pow}_number{number_of_biprimes}.pkl", "wb") as file:
        pickle.dump(results, file)

    # results = construct_and_get_info_of_QAOA_modulo_layer_circuit(data, lvl = lvl)
    # cx_gates, u3_gates = get_gates(num_gates)

    