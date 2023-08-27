# Code for the paper "Integer Factorization through Func-QAOA" 

## Introduction

Welcome to the code repository for the paper "Integer Factorization through Func-QAOA." This repository contains the code necessary to reproduce the results and figures presented in the paper.

## Installation

Before running the Jupyter notebooks, you need to install our modified `vqf` package. This is a forked version of the original package with a `pyproject.toml` and `setup.py` files for easy installation. To install it, run the following command in your terminal or command prompt:

```bash
pip install git+https://github.com/Mostafa-Atallah2020/vqf.git#egg=vqf
```

Additionally, make sure to install the required packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage

To use the code properly, follow these steps:

1. Start by installing the required packages and the modified `vqf` package using the installation instructions provided above.

2. Navigate to the `\examples\` directory. Inside this directory, you will find two Jupyter notebooks:

    * `Effective space for VQF clauses.ipynb`: This notebook is used for generating Figure 4 in the paper. It provides examples and demonstrates the reduction of space for VQF clauses.

    * `compression ratios.ipynb`: This notebook is used for generating Figure 5 in the paper. It includes code for calculating compression ratios related to the topic of integer factorization.

## System Information

The code in this repository was developed using Python 3.11.4 on Windows 10.

## Contact

If you have any questions, suggestions, or inquiries related to the code or this repository, please feel free to contact **Mostafa Atallah** at matallah@sci.cu.edu.eg.


