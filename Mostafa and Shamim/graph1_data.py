from time import time

# import numpy as np
import csv 
from graph1_alt_func import assess_number_of_unknowns, create_clauses

if __name__ == "__main__":  
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--maxpow", type=int, default=10, required=False)
    parser.add_argument("-n", "--number", type=int, default=100, required=False)
    parser.add_argument("-r", "--replace", action="store_true")
    parser.add_argument("--dirin", type=str, default="final_data_biprimes")
    parser.add_argument("--dirout", type=str, default="data_processing")
    args = parser.parse_args()

    number_of_biprimes = args.number
    max_pow = args.maxpow
    biprimes = []
    filename = f"./{args.dirin}/biprimes_maxpow{max_pow}_number{number_of_biprimes}.csv"
    with open(filename, 'r') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        header = next(csvreader)
        # extracting each data row one by one
        for row in csvreader:
            int_row = [int(i) for i in row]
            biprimes.append(int_row)

    # biprimes = np.genfromtxt(
    #     f"./{args.dirin}/biprimes_maxpow{max_pow}_number{number_of_biprimes}.csv",
    #     delimiter=",",
    #     skip_header=1,
    #     dtype="int",
    # )

    file_name_with_preprocessing = (
        f"./{args.dirout}/preprocessing_{max_pow}_results.csv"
    )
    file_name_no_processing = f"./{args.dirout}/no_preprocessing_{max_pow}.csv"

    qubits_required_no_preprocessing = []
    qubits_required_with_preprocessing = []

    print(f"Maximum Power: {max_pow}, Number of Biprimes: {number_of_biprimes}")
    t = time()
    for bi in biprimes:
        p, q, m = bi

        if p > q:
            print(f"Number {m} being considered")

            p_dict, q_dict, z_dict, _ = create_clauses(
                m, p, q, apply_preprocessing=False, verbose=False
            )
            x, z = assess_number_of_unknowns(p_dict, q_dict, z_dict)
            result = [p, q, m, x, z]
            if result not in qubits_required_no_preprocessing:
                qubits_required_no_preprocessing.append(result)

            p_dict, q_dict, z_dict, _ = create_clauses(
                m, p, q, apply_preprocessing=True, verbose=False
            )
            x, z = assess_number_of_unknowns(p_dict, q_dict, z_dict)
            result = [p, q, m, x, z]
            if result not in qubits_required_with_preprocessing:
                qubits_required_with_preprocessing.append(result)
    
    with open(file_name_no_processing, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["p", "q", "m", "unknowns","carry_bits"])
        csvwriter.writerows(qubits_required_no_preprocessing)

    with open(file_name_with_preprocessing, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["p", "q", "m", "unknowns","carry_bits"])
        csvwriter.writerows(qubits_required_with_preprocessing)

    # np.savetxt(
    #     file_name_no_processing,
    #     qubits_required_no_preprocessing,
    #     delimiter=",",
    #     fmt="%.d",
    #     header="p,q,m,unknowns,carry_bits",
    #     comments="",
    # )

    # np.savetxt(
    #     file_name_with_preprocessing,
    #     qubits_required_with_preprocessing,
    #     delimiter=",",
    #     fmt="%.d",
    #     header="p,q,m,unknowns,carry_bits",
    #     comments="",
    # )

    print(f"Computation finished ({time()-t} seconds)")
