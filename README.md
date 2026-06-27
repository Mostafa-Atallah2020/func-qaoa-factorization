# Code for the paper "Towards Integer Factorization through Program-based Quantum Approximate Optimization Algorithm"

## Installation

Before running the Jupyter notebooks, you need to install our modified `vqf`
package. This is a forked version of the original package with `pyproject.toml`
and `setup.py` files for easy installation. To install it, run the following
command in your terminal or command prompt:

```bash
pip install git+https://github.com/Mostafa-Atallah2020/vqf.git#egg=vqf
```

Additionally, make sure to install the required packages listed in
`requirements.txt`:

```bash
pip install -r requirements.txt
```

The code in this repository was originally developed using Python 3.11.4 on
Windows 10, and has also been verified on Python 3.12.10 (Windows 11 Pro,
build 26200) with qiskit 2.x.

## Usage

To use the code properly, follow these steps:

1. Install the required packages and the modified `vqf` package using the
   installation instructions above.

2. Navigate to the `examples/` directory. You will find three Jupyter notebooks:

    * `state_preparation_circuits.ipynb`: generates the Figure 4 circuit
      diagrams. It demonstrates the clause space reduction and the resulting
      state-preparation circuits.

    * `compression_ratios.ipynb`: generates the Figure 5 compression-ratio
      plots over a set of large biprimes.

    * `qaoa_simulation_results.ipynb`: visualizes the Prog-QAOA simulation
      sweep, success probability vs depth, gate-count and depth scaling, the
      search-space reduction, and the simulation runtime.

3. To produce the simulation data for the third notebook, run the sweep CLI,
   which writes a timestamped folder under `results/`:

    ```bash
    python scripts/run_qaoa_simulation.py -m 15 21 35 --multipliers hrs \
        -p 1 2 3 4 5 --seeds 5
    ```

   On Windows you can use the batch wrapper `scripts/run_full_sweep.bat`. The
   run is resumable: re-running skips configurations already present in the CSV.
   Then open `qaoa_simulation_results.ipynb`, which loads the latest run folder
   and regenerates every figure.

## Citation

If you use this code, please cite:

```bibtex
@misc{atallah2023integerfactorizationfuncqaoa,
      title={Towards Integer Factorization through Program-based Quantum Approximate Optimization Algorithm},
      author={Mostafa Atallah and Haemanth Velmurugan and Rohan Sharma and Siddhant Midha and Shamim Al Mamun and Ludmila Botelho and Adam Glos and Özlem Salehi},
      year={2023},
      eprint={2309.15162},
      archivePrefix={arXiv},
      primaryClass={quant-ph},
      url={https://arxiv.org/abs/2309.15162},
}
```

## Contact

If you have any questions, suggestions, or inquiries related to the code or this
repository, please feel free to contact **Mostafa Atallah** at
matallah@sci.cu.edu.eg.
