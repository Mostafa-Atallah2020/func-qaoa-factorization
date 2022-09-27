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

def get_primes_in_range(start, end):
    primes = []
    for p in range(start, end):
        if is_prime(p, p):
            primes.append(p)

    return primes

def get_primes(max_power):
    # Choose numbers uniformly between minimal and maximal value in log scale
    int_lst = np.logspace(1, max_power, max_power)
    primes_lst = []

    for n in int_lst:
        k1 = int(np.exp((np.log10(n)/2) - 1))
        k2 = int(np.exp((np.log10(n)/2) + 1))

        # sample two integers n1,n2 from [k1,k2]
        primes = get_primes_in_range(k1, k2)
        n1, n2 = np.random.choice(primes, 2, replace=False)

        for p in primes:
            # take the smallest prime number p1 larger than n1
            if p >= n1:
                p1 = p
            # take the smallest prime number p2 larger than n2
            if p >= n2:
                p2 = p

        primes_lst.append([p1, p2, p1*p2])

    return primes_lst
    
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
