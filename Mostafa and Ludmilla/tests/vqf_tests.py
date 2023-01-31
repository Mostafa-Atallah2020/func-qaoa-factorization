import sys
# include path to the vqf module.
# TODO: add a relative path that work on every system.
sys.path.append(
    "/media/psi-boi/main/school&workshops/QWorld/QINTERN/QINTERN22/repo/12_Integer-factorization-through-QAOA/Mostafa and Ludmilla"
)

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

def test_apply_rule_2():
    ## Given
    known_expressions = {}
    p, q = symbols('p q')
    clause = p + q - 1
    ## When
    known_expressions = apply_rule_2(clause, known_expressions)
    ## Then
    assert known_expressions[p*q] == 0
    assert known_expressions[p] == 1 - q


def test_apply_rule_3():
    ## Given
    known_expressions = {}
    q = symbols('q')
    clause = 2 - 2*q
    ## When
    known_expressions = apply_rule_3(clause, known_expressions)
    ## Then
    assert known_expressions[q] == 1


def test_apply_rules_4_and_5():
    ## Given
    known_expressions = {}
    q_0, q_1, p_0, p_1 = symbols('q_0 q_1 p_0 p_1')
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
    q_0, q_1, p_0, p_1 = symbols('q_0 q_1 p_0 p_1')
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
    q = symbols('q')
    clause = q - 1
    ## When
    known_expressions = apply_rules_4_and_5(clause, known_expressions)
    ## Then
    assert known_expressions[q] == 1
    assert len(known_expressions) == 1
