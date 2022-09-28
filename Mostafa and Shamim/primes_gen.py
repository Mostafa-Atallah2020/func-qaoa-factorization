import time
import random
import math

import numpy as np

def miller_test(d, n):
    a = int(2 + random.randint(1, n - 4))
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

def is_prime_probs(n, reps=1):
    '''
    checks for primality using the probabilistic method
    '''
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

'''
def get_primes_in_range(start, end):
    primes = []
    for p in range(start, end):
        if is_prime_probs(p, 10):
            primes.append(p)

    return primes

def get_primes(max_power):
    # Choose numbers uniformly between minimal and maximal value in log scale
    int_lst = np.logspace(1, max_power, max_power, base=2)
    primes_lst = []

    for n in int_lst:
        n = int(n)
        #k1 = int(10 ** ((math.log10(n)/2) - 1))
        k1 = int(2 ** ((math.log2(n)/2) - 1))
        #k2 = int(10 ** ((math.log10(n)/2) + 1))
        k2 = int(2 ** ((math.log2(n)/2) + 1))
        # sample two integers n1,n2 from [k1,k2]
        #primes = get_primes_in_range(k1, k2)
        integers = range(k1, k2)
        n1, n2 = np.random.choice(integers, 2, replace=False)

        for k in np.arange(n1, 2*k2):
            k = int(k)
            if is_prime(k, 10):
                p1 = k
        
        for k in np.arange(n2, 2*k2):
            k = int(k)
            if is_prime(k, 10):
                p2 = k

        primes_lst.append([k1, k2, n1, n2, p1, p2, p1*p2])

    return primes_lst
'''

def is_prime_deter(n):
    '''
    checks for primality using the deterministic method
    '''
    if (n == 2) or (n == 3):
        return True
    
    if (n % 2) or (n < 2):
        return False

    lim = int(math.sqrt(n)) + 1

    for i in range(3, lim, 2):
        if (n % i) == 0:
            return False

    return True

def get_primes_SOE(n):
    '''
    get primes smaller than or equal to n using Sieve of Eratosthenes method with time complexiety O(n*log(log(n)))
    https://www.geeksforgeeks.org/sieve-of-eratosthenes/
    '''
    n = int(n)
    prime = [True for i in range(n + 1)]
    p = 2
    primes_lst = []

    while (p ** 2) <= n:
        if prime[p]:
            for i in range(p ** 2, n + 1, p):
                prime[i] = False
        p += 1

    for p in range(2, n+1):
        if prime[p]:
            primes_lst.append(p)

    return primes_lst

def get_biprimes(threshold):
    n = int(np.sqrt(threshold))
    primes = get_primes_SOE(n)
    primes = primes[1:]
    biprimes = []

    for p in primes:
        for q in primes:
            if p < q:
                continue
            m = p * q
            if m > threshold:
                continue
            biprimes.append([p, q, m])

    return biprimes


if __name__ == "__main__":

    threshold = 1e9

    start = time.perf_counter()
    biprimes = get_biprimes(threshold)
    #primes = get_primes(power)
    end = time.perf_counter()
    tottime = end - start
    
    np.savetxt(
        f"./data/biprimes{int(threshold)}.csv",
        np.array(biprimes),
        delimiter=",",
        fmt="%.d",
        header="p, q, m=p*q",
        comments="",
    )
    
    print(f"total time = {tottime} s")
