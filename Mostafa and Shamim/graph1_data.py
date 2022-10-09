from graph1_alt_func import create_clauses, assess_number_of_unknowns
import numpy as np

def main(threshold):

    file_name_with_preprocessing = "./data/preprocessing_"+str(int(threshold))+"_results.csv"
    file_name_no_processing = f"./data/no_preprocessing{int(threshold)}.csv"

    biprimes = np.genfromtxt(f"./data/biprimes{int(threshold)}.csv",
                            delimiter=',',
                            skip_header=1,
                            dtype='int')

    qubits_required_no_preprocessing = []
    qubits_required_with_preprocessing = []

    for bi in biprimes:
        p = bi[0]
        q = bi[1]
        m = bi[2]

        try:
            p_dict, q_dict, z_dict, _ = create_clauses(m, p, q, apply_preprocessing=False, verbose=False)
            x, z = assess_number_of_unknowns(p_dict, q_dict, z_dict)
            qubits_required_no_preprocessing.append([m, x, z])

            p_dict, q_dict, z_dict, _ = create_clauses(m, p, q, apply_preprocessing=True, verbose=False)
            x, z = assess_number_of_unknowns(p_dict, q_dict, z_dict)
            qubits_required_with_preprocessing.append([m, x, z])

        except:
            continue

    
    np.savetxt(file_name_no_processing, 
            np.array(qubits_required_no_preprocessing), 
            delimiter=",", fmt='%.d', 
            header='m,unknowns,carry_bits', comments='')

    np.savetxt(file_name_with_preprocessing, 
            np.array(qubits_required_with_preprocessing), 
            delimiter=",", fmt='%.d', 
            header='m,unknowns,carry_bits', comments='')


if __name__ == '__main__':
    import time
    import sys
    #threshold = sys.maxsize
    threshold = 1e10

    start = time.perf_counter()
    main(threshold)
    end = time.perf_counter()
    tottime = end - start

    print(f'Total time: {tottime/60} min')
