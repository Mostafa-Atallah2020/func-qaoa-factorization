import matplotlib.pyplot as plt


plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 12
})

def make_single_plot(n,ydata,name):
    name_plot = name.replace(" ","_")
    plt.figure(figsize=(3.5,2.625))
    plt.plot(n, ydata)
    plt.title(f"Plot for the number of {name} against n")
    plt.xlabel("n")
    plt.ylabel(f"Number of {name}")
    plt.grid()
    plt.savefig(f"{name_plot}_vs_n.png")


def make_plots(n, num_qubits=None,num_clbits=None,depths=None,cx_gates=None,u3_gates=None):

    if num_qubits:
        make_single_plot(n,num_qubits,"qubits")
    if num_clbits:
        make_single_plot(n,num_clbits,"classical bits")
    if depths:
        make_single_plot(n,num_clbits,"circuit depth")
    if cx_gates:
        make_single_plot(n,cx_gates,"cx gates")
    if u3_gates:
        make_single_plot(n,u3_gates,"u3 gates")

    
