from numpy import pi

# importing Qiskit
from qiskit import (
    Aer,
    ClassicalRegister,
    QuantumCircuit,
    QuantumRegister,
    assemble,
    transpile,
)


def swap_circuit(quantum_circuit, qubit_array):
    nqubits = len(qubit_array)
    for i in range(int(len(qubit_array) / 2)):
        quantum_circuit.swap(qubit_array[i], qubit_array[nqubits - 1 - i])
    return quantum_circuit


def qft_routine(quantum_circuit, qubit_array):
    if len(qubit_array) == 1:
        quantum_circuit.h(qubit_array[0])
        return quantum_circuit
    last_qubit = qubit_array[-1]
    quantum_circuit.h(last_qubit)
    for qubit in reversed(qubit_array[:-1]):
        quantum_circuit.cp(2 * pi / (2 ** (last_qubit - qubit + 1)), qubit, last_qubit)
    quantum_circuit = qft_routine(quantum_circuit, qubit_array[:-1])
    return quantum_circuit


def QFT(quantum_circuit, qubit_array, swap=True):
    if swap:
        quantum_circuit = swap_circuit(quantum_circuit, qubit_array)
    return qft_routine(quantum_circuit, qubit_array)


def IQFT(quantum_circuit, qubit_array, swap=True):
    if swap:
        quantum_circuit = swap_circuit(quantum_circuit, qubit_array)
    quantum_circuit.h(qubit_array[0])
    for current_qubit_index in range(1, len(qubit_array)):
        for qubit_index in range(current_qubit_index):
            quantum_circuit.cp(
                -pi / (2 ** (qubit_index + 1)),
                qubit_array[current_qubit_index],
                qubit_array[current_qubit_index - qubit_index - 1],
            )
        quantum_circuit.h(qubit_array[current_qubit_index])
    return quantum_circuit


def adder_block(number_of_qubits, multiplier):
    qc = QuantumCircuit(2 * number_of_qubits)
    for i in range(number_of_qubits, 2 * number_of_qubits):
        index = i - number_of_qubits
        for j in range(index, number_of_qubits):
            qc.cp(2 ** (multiplier) * pi / (2 ** (j - index)), j, i)
    return qc


def process_numbers(a, b):
    if len(a) > len(b):
        b = "0" * (len(a) - len(b)) + b
    elif len(b) > len(a):
        a = "0" * (len(b) - len(a)) + b
    a = "0" + a
    b = "0" + b
    return a, b, len(a)


def initialize_circuit(qc, a_num, b_num, n):
    for i in range(n):
        if int(a_num[i]):
            qc.x(i + n)
        if int(b_num[i]):
            qc.x(i)
    return qc


def quantum_adder(a, b):
    a = a
    a_num, b_num, n = process_numbers(a, b)
    a_reg = QuantumRegister(n, "a")
    b_reg = QuantumRegister(n, "b")
    c_reg = ClassicalRegister(n)
    qc = QuantumCircuit(b_reg, a_reg, c_reg)
    qc = initialize_circuit(qc, a_num, b_num, n)
    qc.barrier()
    qc = QFT(qc, range(2 * n)[n:], swap=True)
    qc = swap_circuit(qc, range(2 * n)[n:])
    qc.barrier()
    qc = qc.compose(adder_block(n, 0))
    qc.barrier()
    qc = IQFT(qc, range(2 * n)[n:], swap=True)
    qc.barrier()

    return qc


def measure_adder(qc, n):
    qc.measure(range(2 * n)[n:], range(n))
    sim = Aer.get_backend("aer_simulator")  # Tell Qiskit how to simulate our circuit
    qc = transpile(qc, sim)
    qobj = assemble(qc)
    result = sim.run(qobj).result()
    counts = result.get_counts()
    return list(counts)


def quantum_multiplier(a, b):
    a_num, b_num, n = process_numbers(a, b)
    a_reg = QuantumRegister(n, "a")
    b_reg = QuantumRegister(n, "b")
    zero = QuantumRegister(n, "zero")
    c = ClassicalRegister(n)
    qc = QuantumCircuit(b_reg, a_reg, zero, c)

    qc = initialize_circuit(qc, a_num, b_num, n)
    qc.barrier()

    qc = QFT(qc, range(3 * n)[2 * n :])
    # qc = swap_circuit(qc,range(3*n)[2*n:])
    qc.barrier()
    arr = list(range(3 * n))[n:]
    for i in reversed(range(n)):
        block = adder_block(n, n - 1 - i).to_gate().control(1)
        arr.insert(0, i)
        # print(arr)
        qc.append(block, arr)
        arr = arr[1:]
    qc.barrier()
    qc = IQFT(qc, range(3 * n)[2 * n :])

    return qc


def measure_multiplier(qc, n):
    qc.measure(range(3 * n)[2 * n :], range(n))
    sim = Aer.get_backend("aer_simulator")  # Tell Qiskit how to simulate our circuit
    qc = transpile(qc, sim)
    qobj = assemble(qc)
    result = sim.run(qobj).result()
    counts = result.get_counts()
    return list(counts)
