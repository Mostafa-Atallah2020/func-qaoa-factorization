import time
import random
import math

import numpy as np

def is_prime_miller_test(n):
    # Implementation uses the Miller-Rabin Primality Test
    # The optimal number of rounds for this test is 40
    # See http://stackoverflow.com/questions/6325576/how-many-iterations-of-rabin-miller-should-i-use-for-cryptographic-safe-primes
    # for justification

    # If number is even, it's a composite number

    if n == 2 or n == 3:
        return True

    if n % 2 == 0:
        return False

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2
    for aa in np.arange(2, min(n, math.floor(2*math.log(n)**2))):
        a = int(aa)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def get_primes(max_power, num_biprimes):
    # Choose numbers uniformly between minimal and maximal value in log scale
    int_lst = np.logspace(3, max_power, num_biprimes, base=2)
    int_lst = [int(x) for x in int_lst]
    primes_lst = []

    for i, n in enumerate(int_lst):
        n = int(n)
        #k1 = int(10 ** ((math.log10(n)/2) - 1))
        k1 = max(2, int(2 ** ((math.log2(n)/2) - 1)))
        #k2 = int(10 ** ((math.log10(n)/2) + 1))
        k2 = int(2 ** ((math.log2(n)/2) + 1))
        # sample two integers n1,n2 from [k1,k2]
        #primes = get_primes_in_range(k1, k2)

        n1, n2 = np.random.randint(k1, k2, 2,dtype=np.ulonglong)
        p1, p2 = int(n1), int(n2)
        while not is_prime_miller_test(p1):
            p1 += 1 
        while not is_prime_miller_test(p2):
            p2 += 1 

        primes_lst.append([p1, p2, p1*p2])

    return primes_lst

if __name__ == "__main__":
    import sys
    #threshold = sys.maxsize
    threshold = 1e10 
    max_pow = int(np.log2(threshold))
    t = time.time()
    biprimes = get_primes(max_pow, 100)
    tottime = time.time()-t
    
    np.savetxt(
        f"./data/biprimes{int(threshold)}.csv",
        np.array(biprimes),
        delimiter=",",
        fmt="%.d",
        header="p, q, m=p*q",
        comments="",
    )
    
    print(f"total time = {tottime} s")
