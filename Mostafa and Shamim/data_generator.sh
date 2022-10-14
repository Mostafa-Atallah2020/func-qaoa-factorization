#!/bin/bash

for i in {10..128}
do
    python primes_gen_adam.py --maxpow $i --number 100
    python primes_gen_adam.py --maxpow $i --number 500
done


for i in {10..128}
do
    python graph1_data.py --maxpow $i --number 100
    python graph1_data.py --maxpow $i --number 500
done

