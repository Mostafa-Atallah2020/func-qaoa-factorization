import matplotlib.pyplot as plt
import numpy as np
import csv
from scipy.optimize import curve_fit
import math

def exp_func(x, a, b, c):
    return a * np.power(x, b) + c


def get_data_qubits_biprimes(maxpow):
    file_name_with_preprocessing = (
        f"./data_processing/preprocessing_{maxpow}_results.csv"
    )

    qubits_required_with_preprocessing = []

    with open(file_name_with_preprocessing, "r") as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        header = next(csvreader)
        # qubits_required_with_preprocessing.append(header)
        # extracting each data row one by one
        for row in csvreader:
            int_row = [int(i) for i in row]
            qubits_required_with_preprocessing.append(int_row)

    data_2 = np.asarray(qubits_required_with_preprocessing)
    biprimes = data_2[:, 2]
    qubits = data_2[:, 4]

    return biprimes, qubits


def make_plots(biprimes, qubits, maxpow, which_plot=None, extension ="pdf"):
    red, blue = True, True

    plot_name = f"./plots/reprocessing_{maxpow}"

    xdata = np.asarray(list(map(math.log2,biprimes)))
    ydata = qubits


    assert which_plot in [None, "red", "blue"], "invalid option"
    if which_plot == "red":
        blue = False
    elif which_plot == "blue":
        red = False

    plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 12
    })
    figsize = figsize = (3, 2.5) 
    if red:
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(1, 1, 1)

        popt, pcov = curve_fit(exp_func, xdata, ydata)


        ax1.scatter(biprimes, qubits, label="Classical preprocessing", s=10)
        ax1.plot(
            biprimes,
            exp_func(xdata, *popt),
            "m--",
            label="fit: a=%5.5f, b=%5.5f, c=%5.5f" % tuple(popt),
        )

        ax1.set_xlabel("Biprime to be factored")
        ax1.set_ylabel("Number of qubit required")
        ax1.set_xscale("log", base=2)
        ax1.set_ybound(lower = 0)
        plt.legend()
        plt.savefig(f"{plot_name}_blue_plot.{extension}")

    if blue:
        fig2 = plt.figure()
        ax2 = fig2.add_subplot(1, 1, 1)

        popt, pcov = curve_fit(exp_func, xdata, ydata)


        plt.scatter(xdata, ydata)
        plt.plot(
            xdata,
            exp_func(xdata, *popt),
            "r--",
            label="fit: a=%5.5f, b=%5.5f, c=%5.5f" % tuple(popt),
        )
        ax2.set_xlabel("Maximum Power")
        ax2.set_ylabel("Number of qubit required")
        ax2.set_ybound(lower = 0)

        # print(plt.ylim())
        plt.legend()
        plt.savefig(f"{plot_name}_red_plot.{extension}")



def get_fit(xdata, ydata, num_of_chunks):
    xdata_split = np.array_split(xdata, num_of_chunks)
    ydata_split = np.array_split(ydata, num_of_chunks)

    partial_fit = []
    x = xdata_split[0]
    y = ydata_split[0]
    for i in range(1, num_of_chunks):
        x = np.concatenate((x, xdata_split[i]))
        y = np.concatenate((y, ydata_split[i]))

        interval_start = 2 ** int(x[0])
        interval_end = 2 ** int(x[-1])

        try:

            popt, pcov = curve_fit(exp_func, x, y)

            a = popt[0]
            b = popt[1]
            c = popt[2]

            partial_fit.append([interval_start, interval_end, b])

        except:
            partial_fit.append([interval_start, interval_end, "missing"])
    return partial_fit
