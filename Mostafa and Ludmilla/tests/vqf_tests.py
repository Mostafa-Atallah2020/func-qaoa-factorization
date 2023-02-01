import sys

# include path to the vqf module.
# TODO: add a relative path that work on every system.
sys.path.append(
    "/media/psi-boi/main/school&workshops/QWorld/QINTERN/QINTERN22/repo/12_Integer-factorization-through-QAOA/Mostafa and Ludmilla"
)
import time
from sympy import symbols

from vqf import *


def test_apply_rule_1():
    # Given
    known_expressions = {}
    p, q = symbols("p q")
    clause = p * q - 1
    # When
    known_expressions = apply_rule_1(clause, known_expressions)
    # Then
    assert known_expressions[p] == 1
    assert known_expressions[q] == 1


def test_apply_rule_1_alt():
    # Given
    known_expressions = {}
    p, q = symbols("p q")
    clause = p * q - 1
    # When
    known_expressions = apply_rule_1_alt(clause, known_expressions)
    # Then
    assert known_expressions[p] == 1
    assert known_expressions[q] == 1


def test_run_time_of_apply_rule_1():
    p, q = symbols("p q")
    clause = p * q - 1
    known_expressions = {}

    start_time = time.time()
    apply_rule_1(clause, known_expressions)
    t1 = time.time() - start_time

    start_time = time.time()
    apply_rule_1_alt(clause, known_expressions)
    t2 = time.time() - start_time

    assert t2 < t1, "apply_rule_1_alt should be faster than apply_rule_1."


def test_apply_rule_2():
    ## Given
    known_expressions = {}
    p, q = symbols("p q")
    clause = p + q - 1
    ## When
    known_expressions = apply_rule_2(clause, known_expressions)
    ## Then
    assert known_expressions[p * q] == 0
    assert known_expressions[p] == 1 - q


def test_apply_rule_3():
    ## Given
    known_expressions = {}
    q = symbols("q")
    clause = 2 - 2 * q
    ## When
    known_expressions = apply_rule_3(clause, known_expressions)
    ## Then
    assert known_expressions[q] == 1


def test_apply_rules_4_and_5():
    ## Given
    known_expressions = {}
    q_0, q_1, p_0, p_1 = symbols("q_0 q_1 p_0 p_1")
    clause = q_0 + q_1 + p_0 + p_1
    ## When
    known_expressions = apply_rules_4_and_5(clause, known_expressions)
    ## Then
    assert known_expressions[q_0] == 0
    assert known_expressions[q_1] == 0
    assert known_expressions[p_0] == 0
    assert known_expressions[p_1] == 0

    ## Given
    known_expressions = {}
    q_0, q_1, p_0, p_1 = symbols("q_0 q_1 p_0 p_1")
    clause = q_0 + q_1 + p_0 + p_1 - 4
    ## When
    known_expressions = apply_rules_4_and_5(clause, known_expressions)
    ## Then
    assert known_expressions[q_0] == 1
    assert known_expressions[q_1] == 1
    assert known_expressions[p_0] == 1
    assert known_expressions[p_1] == 1

    ## Given
    known_expressions = {}
    q = symbols("q")
    clause = q - 1
    ## When
    known_expressions = apply_rules_4_and_5(clause, known_expressions)
    ## Then
    assert known_expressions[q] == 1
    assert len(known_expressions) == 1


def test_simplify_clause():
    p = 5
    q = 7
    m = p * q
    energy = get_classical_energy(m)
    known_expressions = {}
    known_expressions = apply_rule_1(energy, known_expressions)

    start = time.time()
    energy1 = simplify_clause(energy, known_expressions)
    t1 = time.time() - start

    start = time.time()
    energy2 = simplify_clause_alt(energy, known_expressions)
    t2 = time.time() - start

    assert energy1 == energy2
    assert t2 < t1
