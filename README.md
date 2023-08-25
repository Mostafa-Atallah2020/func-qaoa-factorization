# Code for the paper "Integer Factorization through Func-QAOA" 

## Introduction

This repository contains the code for the the paper "Integer Factorization through Func-QAOA". 

## Installation

Before running the Jupyter notebooks, you need to install out modified `vqf` package, which is a forked version of the original package with a `pyproject.toml` and `setup.py` files to make it installable without actually changing the code.. To install it, run the following command in your terminal or command prompt:

```bash
pip install git+https://github.com/Mostafa-Atallah2020/vqf.git#egg=vqf
```

Additionally, make sure to install the required packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage

To use the code properly, follow the steps below:

1. First, install the required packages and the modified `vqf` package using the installation instructions provided above.

2. Navigate to the `\examples\` directory to find examples on how to reduce the space for VQF. These examples will help you understand the modifications made for the space-efficient version.

3. Run the Jupyter notebook or Python scripts from the examples to experiment with the code. # TODO: This must be much more precise. This is not meant to be a universal package, but an easy collection of scripts for reviewer to reproduce plots. So more like: 3. run script A.py 4. open and run jupyter B.ipynb, etc.


## Contact

If you have any questions or suggestions regarding the code or this repository, please feel free to reach out to **Mostafa Atallah** (matallah@sci.cu.edu.eg).


