import math
import random
import time
from ast import parse

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
    for aa in range(2, min(n, math.floor(2 * math.log(n) ** 2))):
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


# def my_logspace(start,stop,num_elements,base):
#     step = (start-stop)/num_elements
#     powers = range(start,stop + step,step)
#     my_logspace = [base**x for x in powers]
#     return my_logspace


def get_primes(max_power, num_biprimes):
    # Choose numbers uniformly between minimal and maximal value in log scale
    int_lst = np.logspace(6, max_power, num_biprimes, base=2)
    int_lst = [int(x) for x in int_lst]
    primes_lst = []

    for n in int_lst:
        n = int(n)
        # k1 = int(10 ** ((math.log10(n)/2) - 1))
        k1 = max(2, int(2 ** ((math.log2(n) / 2) - 1)))
        # k2 = int(10 ** ((math.log10(n)/2) + 1))
        k2 = int(2 ** ((math.log2(n) / 2) + 1))

        # sample two integers n1,n2 from [k1,k2]
        # primes = get_primes_in_range(k1, k2)

        # n1, n2 = np.random.randint(k1, k2, 2,dtype=np.ulonglong)
        n1 = random.randint(k1, k2)
        n2 = random.randint(k1, k2)

        p1, p2 = int(n1), int(n2)
        while not is_prime_miller_test(p1):
            p1 += 1
        while not is_prime_miller_test(p2):
            p2 += 1

        primes_lst.append([p1, p2, p1 * p2])
    primes_lst = np.asarray(primes_lst)
    primes_lst = primes_lst[primes_lst[:, 2].argsort()]
    # for x in primes_lst:
    # x[:2] = sorted(x[:2])
    return primes_lst


if __name__ == "__main__":
    import argparse
    import csv
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--maxpow", type=int, default=20, required=False)
    parser.add_argument("-n", "--number", type=int, default=100, required=False)
    parser.add_argument("-r", "--replace", action="store_true")
    parser.add_argument("-d", "--dir", type=str, default="final_data_biprimes")
    args = parser.parse_args()

    # threshold = sys.maxsize
    number_of_biprimes = args.number
    max_pow = args.maxpow

    filename = f"./{args.dir}/biprimes_maxpow{max_pow}_number{number_of_biprimes}.csv"
    if os.path.exists(filename) and not args.replace:
        raise ValueError(f'filename "{filename}" already exists - remove')

    t = time.time()
    biprimes = get_primes(max_pow, number_of_biprimes)
    print(f"Computation finished ({time.time()-t} seconds)")

    with open(filename, "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        # writing the header
        csvwriter.writerow(["p", "q", "m=p*q"])
        # writing the data rows
        csvwriter.writerows(biprimes)

    # np.savetxt(
    #     filename,
    #     np.array(biprimes),
    #     delimiter=",",
    #     fmt="%.d",
    #     header="p, q, m=p*q",
    #     comments="",
    # )
    print(f"Data saved to {filename}")
