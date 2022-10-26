import gc
import os
from graph1_alt_func import create_clauses, assess_number_of_unknowns
import numpy as np
from time import time

if __name__ == '__main__':
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

    biprimes = np.genfromtxt(f"./{args.dirin}/biprimes_maxpow{max_pow}_number{number_of_biprimes}.csv",
                            delimiter=',',
                            skip_header=1,
                            dtype='int')
    print(f"{max_pow} {number_of_biprimes}")
    t = time()
    for bi in biprimes:
        p, q, m = bi

        file_name_with_preprocessing = f"./{args.dirout}/preprocessing_{m}_results.csv"
        if os.path.isfile(file_name_with_preprocessing):
            print(f"Number {m} skipped (file exists)")
            continue
        print(f"Number {m} being considered")
            
        p_dict, q_dict, z_dict, _ = create_clauses(m, p, q, apply_preprocessing=True, verbose=False)
        x, z = assess_number_of_unknowns(p_dict, q_dict, z_dict)
        result = [[p, q, m, x, z]]
        p_dict, q_dict, z_dict, x, z = [None, None, None, None, None]
        # print(np.array(result))
        np.savetxt(file_name_with_preprocessing, 
            result, 
            delimiter=",", fmt='%.d', 
            header='p,q,m,unknowns,carry_bits', comments='')

    print(f"Computation finished ({time()-t} seconds)")
    


