



import math
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit.circuit import Parameter
from qiskit.circuit.library.arithmetic.adders import DraperQFTAdder
import numpy as np

def adder(n):
    
    """
    Input n is the number of qubits needed to represent the largest of two values a and b to be added
    
    This function adds the values stored in registers qr_a(say a) and qr_b(say b).
    b+a is computed and stored in b 
    
    """

    qr_a = QuantumRegister(n, name='a')
    qr_b = QuantumRegister(n, name='b')
    qr_z = QuantumRegister(n+1, name='z')  # stores carry
    qr_x = QuantumRegister(n, name='x')    # ancilla qubits

    # cr_b = ClassicalRegister(n, name='sum')
    # cr_z = ClassicalRegister(n+1, name='carry')
    # cr_x = ClassicalRegister(n, name='ancilla')

    P = dict()
    G = dict()

    qc = QuantumCircuit(qr_a, qr_b, qr_z, qr_x)  # , cr_b, cr_z, cr_x)  


    qc.rccx(qr_a[:n], qr_b[:n], qr_z[1:])
    for i in range(n):
        G[(i,i+1)] = qr_z[i+1]


    qc.cnot(qr_a, qr_b)
    for i in range(n):
        P[(i,i+1)] = qr_b[i]


    ### Implement section3 circuit

    ind  = 0
    for t in range(1, int(math.floor(math.log2(n)))):
        for m in range(1, int(n//2**t)):
            i = 2**t * m
            j = i + 2**(t-1)   
            k = i + 2**t

            qc.rccx(P[(i,j)], P[(j,k)], qr_x[ind])
            P[(i,k)] = qr_x[ind]

            ind += 1


    for t in range(1, int(math.floor(math.log2(n)))+1):
        for m in range(0, int(n//2**t)):
            i = 2**t * m 
            j = i + 2**t
            k = i + 2**(t-1)

            qc.rccx(G[(i,k)], P[(k,j)], G[(k,j)])        
            G[(i,j)] = G[(k,j)]


    for t in range(int(math.floor(math.log2(2*n/3))), 0, -1):
        for m in range(1, (n-2**(t-1))//2**t + 1):
            j = 2**t * m + 2**(t-1)
            k = 2**t * m

            qc.rccx(P[(k,j)], G[(0,k)], G[(k,j)])
            G[(0,j)] = G[(k,j)]


    for t in range(int(math.floor(math.log2(n)))-1, 0, -1):
        for m in range(1, int(n//2**t)):
            i = 2**t * m
            j = i + 2**(t-1)   # 2**t m + 2**(t-1)
            k = i + 2**t

            qc.rccx(P[(i,j)], P[(j,k)], P[(i,k)])        


    qc.cnot(qr_z[1:n], qr_b[1:n])

    qc.x(qr_b[:n-1])

    qc.cnot(qr_a[1:n-1], qr_b[1:n-1])
    

    ### Implement section 3 circuit in reverse

    for t in range(1, int(math.floor(math.log2(n)))):
        for m in range(1, int(n//2**t)):
            i = 2**t * m
            j = i + 2**(t-1)   # 2**t m + 2**(t-1)
            k = i + 2**t

            qc.rccx(P[(i,j)], P[(j,k)], P[(i,k)])


    for t in range(1, int(math.floor(math.log2(2*n/3)))+1):
        for m in range(1, (n-2**(t-1))//2**t + 1):
            j = 2**t * m + 2**(t-1)
            k = 2**t * m

            qc.rccx(P[(k,j)], G[(0,k)], G[(0,j)])


    for t in range(int(math.floor(math.log2(n))), 0, -1):
        for m in range(0, int(n//2**t)):
            i = 2**t * m 
            j = i + 2**t
            k = i + 2**(t-1)

            qc.rccx(G[(i,k)], P[(k,j)], G[(i,j)]) 


    for t in range(int(math.floor(math.log2(n)))-1, 0, -1):
        for m in range(1, int(n//2**t)):
            i = 2**t * m
            j = i + 2**(t-1)   # 2**t m + 2**(t-1)
            k = i + 2**t

            qc.rccx(P[(i,j)], P[(j,k)], P[(i,k)])

    qc.cnot(qr_a[1:n-1], qr_b[1:n-1])

    qc.rccx(qr_a[:n-1], qr_b[:n-1], qr_z[1:n])

    qc.x(qr_b[:n-1])
    
    return qc

def inbuilt_adder(n):
    adder_circ = DraperQFTAdder(n, kind='half')
    return adder_circ

def subtractor(n):
    
    """
    Input n is the number of qubits needed to represent the largest of two values a and b to be subtracted
    
    This function subtracts the values stored in registers qr_a(say a) and qr_b(say b).
    b-a is computed and stored in b
    
    """
        
    qr_a = QuantumRegister(n)
    qr_b = QuantumRegister(n)
    qr_z = QuantumRegister(n+1)
    qr_x = QuantumRegister(n)

    qc = QuantumCircuit(qr_a, qr_b, qr_z, qr_x)
    
    # Complement b
    qc.x(qr_b)

    # Append adder circuit
    adder_circ = adder(n)
    # adder_circ = inbuilt_adder(n)
    
    qc.append(adder_circ, qr_a[:] + qr_b[:] + qr_z[:] + qr_x[:])
    
    # Complement b -> Now b stores b-a
    qc.x(qr_b)
    
    return qc

def adder_subtractor(n):



    
    
    """
    Input n is the number of qubits needed to represent the largest of two values a and b to be added or subtracted
    
    This function adds or subtracts the values stored in registers qr_a(say a) and qr_b(say b).
    b+a is computed and stored in b if ctrl is high(1) and b-a is computed and stored in b if ctrl is low(0)
    
    """
    
    ctrl = QuantumRegister(1)
    qr_a = QuantumRegister(n)
    qr_b = QuantumRegister(n)
    qr_z = QuantumRegister(n+1)
    qr_x = QuantumRegister(n)

    qc = QuantumCircuit(ctrl, qr_a, qr_b, qr_z, qr_x)
    
    # Complement b
    qc.cx(ctrl, qr_b)

    # Append adder circuit
    # adder_circ = adder_rccx(n)
    adder_circ = adder(n)
    # adder_circ = inbuilt_adder(n)
    
    qc.append(adder_circ, qr_a[:] + qr_b[:] + qr_z[:] + qr_x[:])
    
    # Complement both a and b -> b stores b-a if ctrl is high
    qc.cx(ctrl, qr_b)
    
    return qc

def ctrl_add(n):
    
    """
    This function takes the value n, which is the number of bits required to represent a or b and returns
    the conditional adder circuit for them
    
    """
    
    # Defining the Registers for CTRL a and b.
    qr_ctrl = QuantumRegister(1, name = "ctrl")
    qr_b = QuantumRegister(n, name = "b")
    qr_a = QuantumRegister(n, name = "a")
    
    # The quantum circuit
    qc = QuantumCircuit(qr_ctrl, qr_a, qr_b)
    
    # The corresponding gates:
    qc.cx(qr_a[1:], qr_b[1:])
        
        
    for j in range(n-1,1,-1):
        qc.cx(qr_a[j-1], qr_a[j])
        
    qc.rccx(qr_b[:n-1],qr_a[:n-1],qr_a[1:])
        
    for p in range(n-1, 0, -1):
        qc.rccx(qr_ctrl,qr_a[p],qr_b[p])
        qc.rccx(qr_b[p-1],qr_a[p-1],qr_a[p])
        
    qc.rccx(qr_ctrl,qr_a[0], qr_b[0])
    
    
    qc.cx(qr_a[1:n-1], qr_a[2:])
    
    qc.cx(qr_a[1:], qr_b[1:])
    
    return qc

def circuit_info(qc):
    """
    Returns basic info - number of qubits, classical bits, depth, gates about any circuit given as input(qc)
    
    """
    
    qubits = qc.num_qubits
    clbits = qc.num_clbits
    depth = qc.depth()
    gates = dict(qc.count_ops())
    
    return (qubits, clbits, depth, gates)

def dec_to_bin_N(N):
    
    """
    Auxiliary function to convert a number to binary
    
    """
    
    N_bin_str = list(bin(N).replace("0b", ""))    
    N_bin = [int(bit) for bit in N_bin_str]    # convert binary string to list
    
    num_bits_N = len(N_bin)    # find number of bits in binary representation of N
            
    return (N_bin, num_bits_N)


def modulo(n):
    """
    n here is the number of qubits needed to represent the dividend
    
    The circuit computes N%p following non-restoring division algorithm
    
    """
    qr_p = QuantumRegister(n, name='p')     # divisor register
    qr_R = QuantumRegister(n-1, name='r')   # remainder register(also stores the dividend initially)
    qr_Q = QuantumRegister(n, name='q')     # quotient register
    qr_z = QuantumRegister(n)               # Ancilla qubits to store intermediate carry
    qr_x = QuantumRegister(n+1)             # Ancilla qubits 
    
    sub_circ = subtractor(n)
    add_sub_circ = adder_subtractor(n)
    ctrl_adder_circ = ctrl_add(n-1)
    qc = QuantumCircuit(qr_p, qr_R, qr_Q, qr_z, qr_x)
    
    
    # Modulo circuit
    qc.append(sub_circ, qr_p[:] + qr_Q[:] + qr_z[:] + qr_x[:])
    
    for i in range(n-1):
        qc.x(qr_Q[n-i-1])
        qc.append(add_sub_circ, [qr_Q[n-i-1]] + qr_p[:] + qr_R[n-i-2:] + qr_Q[0:n-i-1] + qr_z[:] + qr_x[:])  
    qc.append(ctrl_adder_circ, [qr_Q[0]] + qr_p[:-1] + qr_R[:])
    
    qc.x(qr_Q[0])
    
    return qc

def apply_penalty(n): 
    theta = Parameter('theta') 
    qr_N = QuantumRegister(n-1, name='regN') #register storing the result of the circuit
    qc = QuantumCircuit(qr_N)
    qc.rz(theta, qr_N[:])
    return qc


def inverse_modulo(n):
    qc = modulo(n).inverse()
    return qc


def apply_mixer_hamiltonian(p):
    phi = Parameter('phi') 
    qr_p = QuantumRegister(p, name='p')
    qc = QuantumCircuit(qr_p)
    qc.rx(phi, qr_p[1:p])
    return qc


def QAOA_modulo_layer_circuit(N):
    
    """
    N here is the dividend whose factors are to be found
    
    This function builds one layer of the QAOA circuit to factorize N following the modulo approach
    
    """
    
    N, n = dec_to_bin_N(N)
    n_p = int(np.ceil(0.5*n))   # number of bits needed for divisor register(only 1/2*log(N) or 1/2*n)
    
    # Defining the registers:
    qr_p = QuantumRegister(n, name='p')
    qr_R = QuantumRegister(n-1, name='r')
    qr_Q = QuantumRegister(n, name='q')
    qr_z = QuantumRegister(n)
    qr_x = QuantumRegister(n+1)
    cr = ClassicalRegister(n-1)
    cq = ClassicalRegister(n)
    
    
    # The Quantum Circuit:
    qc = QuantumCircuit(qr_p, qr_R, qr_Q, qr_z, qr_x, cr, cq)
    
    
    # Instantiating the relevant submodules:
    mod = modulo(n)
    r_z = apply_penalty(n)
    inv_mod = inverse_modulo(n)
    r_x = apply_mixer_hamiltonian(n_p)
    
    # The QAOA layer circuit
    
    # Step 1: Initialize circuit with input N and setting a superposition for possible p values:
    N.reverse()
    for i, Ni in enumerate(N[:-1]):
        if Ni:
            qc.x(qr_R[i])      
    if N[-1]:
        qc.x(qr_Q[0])
        
    qc.x(qr_p[0]) #Initialize the LSB to 1
    qc.h(qr_p[1:n_p])   # Create a superpoition of divisors upto 
    
    
    # Building one layer of the QAOA circuit
    
    # Step 2: Compute Modulo
    qc.append(mod, qr_p[:] + qr_R[:] + qr_Q[:] + qr_z[:] + qr_x[:])
    
    # Step 3: Apply penalty - Rz(phi) on remainder
    qc.append(r_z,qr_R[:])   # previously: ###qc.append(r_z,qr_R[:]+[qr_Q[0]])
    
    # Step 4: Uncompute - Apply Inverse Modulo
    qc.append(inv_mod,qr_p[:] + qr_R[:] + qr_Q[:] + qr_z[:] + qr_x[:])
    
    # Step 5: Apply Mixer Hamiltonian - Rx(phi) on p(divisor) registers in superposition.
    qc.append(r_x, qr_p[:n_p])
    
    
#     # Measure
#     qc.measure(qr_R, cr)
#     qc.measure(qr_Q, cq)

    return qc

def construct_and_get_info_of_QAOA_modulo_layer_circuit(N_list,lvl=1):
    
    """
    Function to construct 1 layer of QAOA circuit(ansatz) for factorizing a given input N following modulo approach
    Returns circuit information like number of qubits, gates, classical bits, depth
    
    Input N_list is a list of N values for which the circuits are to be constructed
    
    """
    
    num_qubits = []
    num_clbits = []
    depths = []
    num_gates = []
    n = []


    # Construct circuits and get their information - qubits, depth, gates for all N values in N_list
    for i in N_list:
        print(f"Getting data for {i}...")
        qc = QAOA_modulo_layer_circuit(i)

        # Transpiling
        qc_transpiled = transpile(qc, basis_gates=['u3', 'cx'], optimization_level = lvl)
        num_qubits_i, num_clbits_i, depth_i, num_gates_i = circuit_info(qc_transpiled)
        n_i = int(np.ceil(math.log2(i)))
        
        num_qubits.append(num_qubits_i)
        num_clbits.append(num_clbits_i)
        depths.append(depth_i)
        num_gates.append(num_gates_i)
        n.append(n_i)
        print("Done")

    return num_qubits, num_clbits, depths, num_gates, n

def get_gates(num_gates):
    """
    Function to find number of gates from circuit information
    """
    
    cx_gates = []
    u3_gates = []
# measure_gates = []
    
    for this_dict in num_gates:
        cx_gates.append(this_dict['cx'])
        u3_gates.append(this_dict['u3'])
