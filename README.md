# Code for the paper "Integer Factorization through Func-QAOA" 

## Introduction

This repository contains the code for the the paper "Integer Factorization through Func-QAOA". It is a modified version of the regular VQF algorithm, designed to use less space while maintaining similar performance. This work is a continuation of the original work done by Michal Stechly on the [VQF repository](https://github.com/mstechly/vqf).

## Installation

Before running the Jupyter notebooks, you need to install out modified `vqf` package, which is a forked version of the original package. To install it, run the following command in your terminal or command prompt:

```bash
pip install git+https://github.com/Mostafa-Atallah2020/vqf.git#egg=vqf
```

Note that the original package is not installable, so the forked version includes a `pyproject.toml` and `setup.py` files to make it installable without actually changing the code.

Additionally, make sure to install the required packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage

To use the code properly, follow the steps below:

1. First, install the required packages and the modified `vqf` package using the installation instructions provided above.

2. Navigate to the `\examples\` directory to find examples on how to reduce the space for VQF. These examples will help you understand the modifications made for the space-efficient version.

3. Run the Jupyter notebook or Python scripts from the examples to experiment with the code.

## Contact

If you have any questions or suggestions regarding the code or this repository, please feel free to reach out to **Mostafa Atallah** (matallah@sci.cu.edu.eg).


