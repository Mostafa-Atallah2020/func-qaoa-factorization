import time
import random

import numpy as np

from graph1_alt_func import get_primes_lower_than_n

def miller_test(d, n):
    a = 2 + random.randint(1, n - 4)
    x = pow(a, d, n)

    if (x == 1) or (x == n - 1):
        return True

    while (d != n - 1):
        x = x**2 % n
        d *= 2

        if x == 1:
            return False
        
        if x == n - 1:
            return True
    
    return False

def is_prime(n, reps=1):
    if (n <= 1) or (n == 4):
        return False

    if (n <= 3):
        return True

    d = n - 1

    while (d % 2 == 0):
        d //= 2

    for i in range(reps):
        if miller_test(d, n) == False:
            return False
    
    return True


if __name__ == "__main__":

    threshold = 1e4
    start = time.perf_counter()
    primes = get_primes_lower_than_n(int(np.sqrt(threshold)))
    primes = primes[1:]
    end = time.perf_counter()
    tottime = end - start
    np.savetxt(
        f"./data/primes{int(threshold)}.txt",
        np.array(primes, dtype="int32"),
        delimiter=",",
    )
    print(f"total time = {tottime} s")
