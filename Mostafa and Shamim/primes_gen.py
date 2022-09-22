from multiprocessing.dummy import Pool
import matplotlib.pyplot as plt
import numpy as np
import time
from graph1_alt_func import create_clauses, assess_number_of_unknowns, get_primes_lower_than_n, split_list
import time

if __name__ == '__main__':

    threshold = 1e5
    start = time.perf_counter()
    primes = get_primes_lower_than_n(int(threshold))
    primes = primes[1:]
    end = time.perf_counter()
    tottime = end - start
    np.savetxt(f'./data/primes{int(threshold)}.txt', np.array(primes), delimiter=',')
    print(f"total time = {tottime} s")