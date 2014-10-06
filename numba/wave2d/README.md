# Numba Demo: 2D Wave Equation

This demo shows how Numba simplifies the implementation of a 2D partial
differential equation solver.  The code is both shorter than the NumPy
equivalent and faster.

## How to Run

Run the following from inside this directory to setup a conda environment and run the notebook:

    conda create -n numba_wave2d -c seibert --file requirements.txt
    source activate numba_wave2d
    ipython notebook

(Note that the "seibert" channel is used to fetch the JSAnimation package.)
