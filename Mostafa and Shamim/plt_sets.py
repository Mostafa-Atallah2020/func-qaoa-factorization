import matplotlib.pyplot as plt
import numpy as np
import csv
from scipy.optimize import curve_fit


def exp_func(x, a, b, c):
    return a * np.power(x, b) + c


def get_data_qubits_biprimes(maxpow):
    file_name_with_preprocessing = f"./data_processing/preprocessing_{maxpow}_results.csv"

    qubits_required_with_preprocessing = []

    with open(file_name_with_preprocessing, 'r') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        header = next(csvreader)
        # qubits_required_with_preprocessing.append(header)
        # extracting each data row one by one
        for row in csvreader:
            int_row = [int(i) for i in row]
            qubits_required_with_preprocessing.append(int_row)
    
    data_2 = np.asarray(qubits_required_with_preprocessing)
    biprimes = data_2[:,2]
    qubits  = data_2[:,4]

    return biprimes, qubits


def make_plots(biprimes,qubits,maxpow,which_plot = None):
    red,blue = True,True
    
    plot_name = f"./plots/reprocessing_{maxpow}"

    xdata = np.log2(biprimes)
    ydata = qubits

    popt, pcov = curve_fit(exp_func, xdata, ydata)

    assert which_plot in [None, 'red', 'blue'], "invalid option"
    if which_plot == 'red':
        blue = False
    elif which_plot == 'blue':
        red = False

    if red:
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(1, 1, 1)

        ax1.scatter(biprimes, qubits, label="Classical preprocessing", s=10)
        plt.plot(
            biprimes,
            exp_func(np.log2(ydata), *popt),
            "--",
            label="fit: a=%5.5f, b=%5.5f, c=%5.5f" % tuple(popt),
        )

        ax1.set_xlabel("Biprime to be factored")
        ax1.set_ylabel("Number of qubit required")
        ax1.set_xscale("log", base=2)
        plt.legend()
        plt.savefig(f"{plot_name}_blue_plot.png")

    if blue:
        fig2 = plt.figure()
        ax2 = fig2.add_subplot(1, 1, 1)

        plt.scatter(xdata, ydata)
        plt.plot(
            xdata,
            exp_func(xdata, *popt),
            "r--",
            label="fit: a=%5.5f, b=%5.5f, c=%5.5f" % tuple(popt),
        )
        ax2.set_xlabel("Biprime to be factored")
        ax2.set_ylabel("Number of qubit required")
        plt.legend()
        plt.savefig(f"{plot_name}_red_plot.png")


def get_fit(xdata,ydata,num_of_chunks):
    xdata_split = np.array_split(xdata, num_of_chunks)
    ydata_split = np.array_split(ydata, num_of_chunks)

    partial_fit = []
    x = xdata_split[0]
    y = ydata_split[0]
    for i in range(1,num_of_chunks):
        x = np.concatenate((x,xdata_split[i]))
        y = np.concatenate((y,ydata_split[i]))

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
