import pdb
import matplotlib.pyplot as plt
import numpy as np
import time
import inspect, os, sys
from graph1_alt_func import create_clauses, assess_number_of_unknowns, get_primes_lower_than_n

def main(threshold = 1e5):
    primes = get_primes_lower_than_n(int(np.sqrt(threshold)))
    primes = primes[1:]

    qubits_required_no_preprocessing = []
    qubits_required_with_preprocessing = []
    initial_time = time.time()
    # file_name = "preprocessing_full_results.csv"
    # plot_name = "reprocessing_full_plot.png"
    file_name = "./data/preprocessing_"+str(threshold)+"_results.csv"
    plot_name = "./data/reprocessing_"+str(threshold)+"_plot.png"

    for p in primes:
        for q in primes:
            if p < q:
                continue
            m = p * q
            if m > threshold:
                continue
            start_time = time.time()

            p_dict, q_dict, z_dict, _ = create_clauses(
                m, p, q, apply_preprocessing=True, verbose=False
            )
            x, z = assess_number_of_unknowns(p_dict, q_dict, z_dict)
            qubits_required_with_preprocessing.append([m, x, z])

            end_time = time.time()
            t = np.round(end_time - start_time, 3)
            # print(p, q, m, x, z, t, "    ")#, end="\r")

            np.savetxt(
                file_name,
                np.array(qubits_required_with_preprocessing),
                delimiter=",",
                fmt="%.d",
                header="m,unknowns,carry_bits",
                comments="",
            )

    qubits_required_no_preprocessing = np.genfromtxt(
        "./data/no_preprocessing.csv", skip_header=1, delimiter=","
    )
    qubits_required_with_preprocessing = np.genfromtxt(
        "./data/preprocessing_"+str(threshold)+"_results.csv", skip_header=1, delimiter=","
    )
    print("Total time:", np.round((end_time - initial_time) / 60, 3), "[min]")

    data_1 = np.array(qubits_required_no_preprocessing)
    data_2 = np.array(qubits_required_with_preprocessing)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(data_1[:, 0], data_1[:, 1], label="No classical preprocessing", s=10)
    ax.scatter(data_2[:, 0], data_2[:, 1], label="Classical preprocessing", s=10)
    ax.set_xlabel("Biprime to be factored")
    ax.set_ylabel("Number of qubit required")
    ax.set_xscale('log')
    plt.legend()
    plt.savefig(plot_name)
    plt.show()


if __name__ == '__main__':
    # benchmarking the performance for the code that generate graph1
    import cProfile, pstats
    profiler = cProfile.Profile()
    profiler.enable()

    threshold = 1e3
    main(threshold=threshold)

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.dump_stats("./data/benchmark"+str(threshold)+".dmp") # you can visualize a .dmp file using snakeviz
    stats.print_stats()
