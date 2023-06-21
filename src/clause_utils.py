import numpy as np
from tabulate import tabulate
import pandas as pd
from sympy import (
    Add,
    Mul,
    Number,
    Symbol,
    sympify,
)

import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table


def display_dataframe_as_image(df, output_filename):
    fig, ax = plt.figure(figsize=(8, 6)).subplots()
    ax.axis("off")
    table = Table(
        cellText=df.values.tolist(), colLabels=df.columns.tolist(), loc="center"
    )
    ax.add_table(table)
    plt.savefig(output_filename, bbox_inches="tight")


def save_dataframe_as_pdf(df, output_filename):
    data = [df.columns.to_list()] + df.values.tolist()
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    table = Table(data)
    elements = [table]
    doc.build(elements)


def convert_to_dataframe(data, columns=["Key", "Value"]):
    """
    Convert a dictionary to a DataFrame.

    Args:
    -----

        `data` (`dict`): The dictionary to be converted.

    Returns:
    --------

        `pandas.DataFrame`: The resulting DataFrame.

    """
    df = pd.DataFrame(data.items(), columns=columns)
    return df


def merge_dictionaries(*dicts):
    """
    Merge multiple dictionaries into a single dictionary.

    Args:
    -----

        `*dicts`: Multiple dictionaries to be merged.

    Returns:
    --------

        `dict`: Merged dictionary containing all the key-value pairs from the input dictionaries.

    """
    merged_dict = {}

    for dictionary in dicts:
        merged_dict.update(dictionary)

    return merged_dict


def find_non_matching_values(dictionary):
    """
    Find key-value pairs in a dictionary where the key is not equal to the value.

    Args:
    -----

        `dictionary` (`dict`): The dictionary to search for non-matching values.

    Returns:
    --------

        `dict`: Dictionary containing key-value pairs where the key is not equal to the value.

    """
    non_matching_values = {}

    for key, value in dictionary.items():
        if key != value:
            non_matching_values[key] = value

    return non_matching_values


def print_table(data):
    """
    Print a dictionary in tabular form.

    Args:
    -----

        `data` (`dict`): The dictionary to be printed as a table.

    """
    # Convert dictionary to list of lists
    table = [[key, value] for key, value in data.items()]

    # Print table
    print(tabulate(table, headers=["Key", "Value"]))


def get_key_by_value(dictionary, value):
    """
    Get the key associated with a specific value in a dictionary.

    Args:
    -----

        `dictionary` (`dict`): The dictionary to search for the value.
        `value`: The value to search for in the dictionary.

    Returns:
    --------

        Key associated with the specified value, or None if the value is not found in the dictionary.

    """
    for key, val in dictionary.items():
        if val == value:
            return key
    return None  # Value not found


def create_merged_dict(dict1, dict2):
    """
    Create a new dictionary by merging values from two dictionaries.

    The function takes two dictionaries as input and returns a new dictionary
    where the keys are the values from the first dictionary and the values are
    the corresponding values from the second dictionary.

    Args:
    -----

        `dict1` (`dict`): The first dictionary.
        `dict2` (`dict`): The second dictionary.

    Returns:
    --------

        `dict`: A new dictionary with merged values.

    Examples:
    ---------

        >>> dict1 = {'apple': 'fruit', 'carrot': 'vegetable', 'banana': 'fruit'}
        >>> dict2 = {'fruit': 'red', 'vegetable': 'orange'}
        >>> merged_dict = create_merged_dict(dict1, dict2)
        >>> merged_dict
        {'fruit': 'red', 'vegetable': 'orange'}

    """
    merged_dict = {}
    for key, value in dict1.items():
        merged_dict[value] = dict2[key]
    return merged_dict


def create_dictionary(m):
    m_bin = bin(m)[2:][::-1]
    m_dict = {}
    for i, value in enumerate(m_bin):
        m_dict[i] = int(value)
    p_dict = {}
    p_dict[0] = 1
    for i in range(1, int(np.ceil(len(m_bin) / 2))):
        p_dict[i] = Symbol("p" + str(i))
    p_dict[
        int(np.ceil(len(m_bin) / 2)) - 1
    ] = 1  # length half of m is being held.here need some generializtion to check out bit length of p and q optimum.

    q_dict = {}
    q_dict[0] = 1
    for i in range(1, int(np.ceil(len(m_bin) / 2))):
        q_dict[i] = Symbol("q" + str(i))
    q_dict[int(np.ceil(len(m_bin) / 2)) - 1] = 1

    n = len(m_bin) + int(np.ceil(len(m_bin) / 2)) - 1
    z_dict = {}
    for i in range(n):
        for j in range(i + 1):
            if i != j:
                if i >= len(m_bin):
                    pass
                elif j == 0:
                    pass
                else:
                    if i - j >= int(np.ceil(len(m_bin) / 2)) - 1:
                        z_dict[(j, i)] = 0

                    else:
                        z_dict[(j, i)] = Symbol("z" + str(j) + str(i))

        z_dict[(len(m_bin) - 4, len(m_bin) - 1)] = 0
    return m_dict, p_dict, q_dict, z_dict


def max_sum(clause):
    max = 0
    if clause.func == Add:
        for t in clause.args:
            if isinstance(t, Number):
                max = max + int(t)
            # elif isinstance(t, Number) and int(t) < 0:
            #    max -= int(t)
            # print(max)

            if t.func == Mul:
                if isinstance(t.args[0], Symbol):  ###changed  from  previous one
                    max = max + 1

                if isinstance(t.args[0], Number) and t.args[0] > 0:
                    max = max + (int(t.args[0]))

                if isinstance(t.args[0], Number) and t.args[0] < 0:
                    max = max + 0

                if isinstance(t.args[0], Number) and t.args[0] < 0:

                    pass
            if t.func == Symbol:

                max = max + 1

            # if isinstance(t ,Symbol):
            #   max=max+1

            """if   isinstance(t, Number) :
                max = max+ int(t)
            #elif isinstance(t, Number) and int(t) < 0:
            #    max -= int(t) """

            # else :
            #   max = max+1

    elif clause.func == Mul:
        if isinstance(clause.args[0], Number) and clause.args[0] > 0:
            max = max + int(clause.args[0])
        if isinstance(clause.args[0], Number) and clause.args[0] < 0:
            max = max + int(0)

        else:
            max = max + 1

    elif clause.func == Symbol:
        max = 1
    elif isinstance(clause, Number):
        max = max + int(clause)

    return max


def create_dictionary_robust(m):
    m_bin = bin(m)[2:][::-1]
    m_dict = {}
    for i, j in enumerate(m_bin):
        m_dict[i] = int(j)

    p_dict = {}
    p_dict[0] = 1

    for i in range(1, int(np.ceil(len(m_bin) / 2))):
        p_dict[i] = Symbol("p" + str(i))
    p_dict[
        int(np.ceil(len(m_bin) / 2)) - 1
    ] = 1  # length half of m is being held.here need some generializtion to check out bit length of p and q optimum.

    q_dict = {}
    q_dict[0] = 1
    for i in range(1, int(np.ceil(len(m_bin) / 2))):
        q_dict[i] = Symbol("q" + str(i))
    q_dict[int(np.ceil(len(m_bin) / 2)) - 1] = 1

    n = len(m_bin) + int(np.ceil(len(m_bin) / 2)) - 1
    z_dict1 = {}
    z_dict2 = {}

    for i in range(2, len(m_bin)):
        for j in range(i - int(np.floor(np.log2(i))), i):
            if i != j:
                z_dict1[(j, i)] = Symbol("z" + str(j) + str(i))

    for i in range(1, len(m_bin) - 1):
        for j in range(i, i + len(bin(i)[2:][::-1]) + 1):
            if i != j and j <= len(m_bin):
                z_dict2[(i, j)] = Symbol("z" + str(i) + str(j))

    return m_dict, p_dict, q_dict, z_dict2


def create_clause1(m, p, q, z):
    """there is another  version  of it called create_clause2 where we have taken all the z.get possible  and then we have let our rule 1 to cut all extra z"""
    clauses = []
    clauses1 = []
    z_zero = {}
    n = len(m) + int(np.ceil(len(m) / 2)) - 1
    for i in range(n):
        clause = 0
        for j in range(i + 1):
            clause += q.get(j, 0) * p.get(i - j, 0)
        # clause  += - m.get(i,0)
        for j in range(i + 1):
            clause += z.get((j, i), 0)

        if type(clause) == int:
            clause = sympify(clause)
        if clause != 0:
            max_sum1 = max_sum(clause)
            if max_sum1 != 0:
                max_carry = int(np.floor(np.log2(max_sum1)))
            else:
                max_carry = 0
        for j in range(len(z)):
            if j - i > max_carry:
                if z.get((i - 1, j), 0) != 0:
                    z[(i - 1, j)] = 0
                    z_zero["z" + str(i - 1) + str(j)] = 0
        clause += -m.get(i, 0)
        for j in range(i + 1, i + 5):
            if j - i <= max_carry + 1:
                clause += -(2 ** (j - i)) * z.get((i, j), 0)

        if clause == 0:
            clause = sympify(clause)
        clauses.append(clause)

    # for clause in clauses:
    #   for keys in z_zero:
    #       clause=str(clause).replace(z_zero[keys],'0')
    #   clauses1.append(clause)

    return clauses


def create_clause2(m, p, q, z):
    """there is another  version  of it called create_clause2 where we have taken all the z.get possible  and then we have let our rule 1 to cut all extra z values"""
    clauses = []
    clauses1 = []
    z_zero = {}
    n = len(m) + int(np.ceil(len(m) / 2)) - 1
    for i in range(n):
        clause = 0
        for j in range(i + 1):
            clause += q.get(j, 0) * p.get(i - j, 0)
        # clause  += - m.get(i,0)
        for j in range(i + 1):
            clause += z.get((j, i), 0)

        if type(clause) == int:
            clause = sympify(clause)
        if clause != 0:
            max_sum1 = max_sum(clause)
            if max_sum1 != 0:
                max_carry = int(np.ceil(np.log2(max_sum1)))

            else:
                max_carry = 0
        """for j in range(i+1):
            if j-i > max_carry:
                if z.get((i-1, j), 0) != 0:
                    z[(i-1, j)] = 0
                    z_zero['z'+str(i-1)+str(j)] = 0 """
        clause += -m.get(i, 0)
        for j in range(i + 1, i + max_carry + 1):
            if j - i <= max_carry + 1:
                clause += -(2 ** (j - i)) * z.get((i, j), 0)

        if clause == 0:
            clause = sympify(clause)
        clauses.append(clause)

    # for clause in clauses:
    #   for keys in z_zero:
    #       clause=str(clause).replace(z_zero[keys],'0')
    #   clauses1.append(clause)

    return clauses


def rule_21(clause, expression):
    if (
        clause.func == Add
        and len(clause.args) == 3
        and len(list(clause.free_symbols)) == 2
    ):
        sub_clause = clause.subs(
            {
                list(clause.free_symbols)[0]: Symbol("x"),
                list(clause.free_symbols)[1]: Symbol("y"),
            }
        )
        rule = Symbol("x") + Symbol("y") - 1
        if sub_clause - rule == 0:
            expression[list(clause.free_symbols)[0] * list(clause.free_symbols)[1]] = 0
            expression[list(clause.free_symbols)[0] + list(clause.free_symbols)[1]] = 1
            """if 'q' in str(list(clause.free_symbols)[0]):
                expression[list(clause.free_symbols)[0]]= 1 - list(clause.free_symbols)[1]
            else :
                expression[lisit(clause.free_symbols)[1]]= 1 - list(clause.free_symbols)[0]"""
    if len(expression) != 0:
        print(("rule21applied"))

    return expression


def rule_31(clause, expression):
    if (
        clause.func == Add
        and len(clause.args) == 2
        and len(list(clause.free_symbols)) == 1
    ):
        sub_clause = clause.subs({list(clause.free_symbols)[0]: Symbol("x")})
        rule = Symbol("x") - 1
        if sub_clause - rule == 0:
            expression[list(clause.free_symbols)[0]] = 1
            """if 'q' in str(list(clause.free_symbols)[0]):
                expression[list(clause.free_symbols)[0]]= 1 - list(clause.free_symbols)[1]
            else :
                expression[list(clause.free_symbols)[1]]= 1 - list(clause.free_symbols)[0]"""
    if len(expression) != 0:
        print(("rule31applied"))

    return expression


def rule_11(clause, expression):
    negative = []

    for t in clause.args:
        if t.func == Mul and isinstance(t.args[0], Number) and t.args[0] < 0:
            negative.append(t)

    if len(negative) > 0:
        for t in negative:
            if -t.args[0] > max_sum(clause):
                var = t / t.args[0]
                expression[var] = 0
    if len(expression) != 0:
        print(("rule11applied"))

    # print (max_sum(clause))

    return expression


def rule_51(clause, known_expressions):

    if clause.func == Add and len(clause.args) == 2:
        if len(clause.args[0].free_symbols) == 0:
            constant_a = clause.args[0]
            if clause.args[1].func == Mul:
                constant_b = clause.args[1].args[0]
                symbol = clause.args[1] / constant_b
                if isinstance(constant_a, Number) and isinstance(constant_b, Number):
                    if constant_a > 0 or constant_b < 0:

                        known_expressions[symbol] = 1
    return known_expressions


def rule_41(clause, expression):
    count = 0
    if clause.func == Add and max_sum(clause) == len(list(clause.free_symbols)):
        for t in clause.args:
            if t.func != Mul:
                expression[t] = 0

    else:
        for t in clause.args:
            if isinstance(t, Number):
                count = count + t
        if clause.func == Add and len(list(clause.free_symbols)) == -count:
            for t in clause.args:
                if t != count:
                    expression[t] = 1


def rule_61(clause, expression):
    if clause.func == Symbol and len(list(clause.free_symbols)) == 1:
        """if isinstance(clause.args[0],Number):
        var= clause / clause.args[0]
        sub_clause=var.subs({list(clause.free_symbols)[0]: Symbol('x')})
        rule= Symbol('x')
        if sub_clause -rule ==0 :
           expression[list(clause.free_symbols)[0]] =0"""

        print(clause.free_symbols)
        sub_clause = clause.subs({list(clause.free_symbols)[0]: Symbol("x")})
        rule = Symbol("x")
        if sub_clause - rule == 0:
            expression[list(clause.free_symbols)[0]] = 0

    if clause.func == Mul and len(list(clause.free_symbols)) == 1:
        var = clause / clause.args[0]
        sub_clause = var.subs({list(clause.free_symbols)[0]: Symbol("x")})
        rule = Symbol("x")
        if sub_clause - rule == 0:
            expression[list(clause.free_symbols)[0]] = 0


def rule_71(clause, expression):
    count = 0
    constant = 0
    negative = []
    if clause.func == Add:
        for t in clause.args:
            if isinstance(t, Number) and int(t) > 0:
                constant = constant + int(t)
                print(type(int(t)))
            if isinstance(t, Symbol):
                count = count + 1
                print(type(count))
            if t.func == Mul:
                if isinstance(t.args[0], Number) and t.args[0] < 0:

                    negative.append(-t.args[0])
                else:

                    count = count + 1

        print(negative)

    if len(negative) > 0 and constant + count == max(negative) and int(count) > 0:
        for t in clause.args:
            if t.func == Mul and isinstance(t.args[0], Number):
                var = t / t.args[0]
                expression[var] = 1
                for i in var.args:
                    expression[i] = 1
            if t.func == Mul and isinstance(t.args[0], Symbol):
                for i in t.args:
                    if isinstance(i, Symbol):
                        expression[i] = 1

    return expression


def rule_81(clause, expression):
    negative = []

    for t in clause.args:
        if t.func == Mul and isinstance(t.args[0], Number) and t.args[0] < 0:
            negative.append(t)

    if len(negative) == 0:
        for t in clause.args:

            expression[t] = 0

    return expression


def rule_sum_equal(clause, expression):
    """finding out the clauses where max negative is ===  maxsum   then checking out they are 1 or 0"""

    negative = []

    for t in clause.args:
        if t.func == Mul and isinstance(t.args[0], Number) and t.args[0] < 0:
            negative.append(t)
    l = []

    if len(negative) > 0:

        for t in negative:
            if -t.args[0] == max_sum(clause):
                var = t / t.args[0]
                expression[var] = 1
                l.append(var)

                for t in negative:
                    var1 = t / t.args[0]
                    if var1 != var:
                        expression[var1] = 0

                for i in clause.args:
                    if (
                        i.func == Mul
                        and isinstance(i.args[0], Symbol)
                        and isinstance(i.args[1], Symbol)
                    ):
                        expression[i.args[0]] = 1
                        expression[i.args[1]] = 1

                for i in clause.args:
                    if isinstance(i, Symbol):
                        expression[i] = 1


def false_clause(clause):
    negative = []

    for t in clause.args:
        if t.func == Mul and isinstance(t.args[0], Number) and t.args[0] < 0:
            negative.append(t)

        if len(negative) == 0:
            for t in clause.args:
                if isinstance(t, Number) and t > 0:
                    return True

    return expression, l


def rule77(clause, expression):
    negative = []

    for t in clause.args:
        if t.func == Mul and isinstance(t.args[0], Number) and t.args[0] < 0:
            negative.append(t)

    if len(negative) == 1:
        for t in clause.args:
            if isinstance(t, Number) and t > 0:
                for t in negative:
                    var = t / t.args[0]
                    expression[var] = 1
    return expression


if __name__ == "__main__":

    m, p, q, z = create_dictionary_robust(291311)
    p2 = create_clause2(m, p, q, z)
    p2

    expression_1 = {}
    renew_clause_1 = []
    for clauses in p2:

        rule_81(clauses, expression_1)

    for clauses in p2:
        renew_clause_1.append(clauses.subs(expression_1).expand())
    renew_clause_1

    expression_2 = {}
    renew_clause_2 = []
    for clauses in renew_clause_1:

        rule_81(clauses, expression_2)

    for clauses in renew_clause_1:
        renew_clause_2.append(clauses.subs(expression_2).expand())
    renew_clause_2

    expression_3 = {}
    renew_clause_3 = []
    for clauses in renew_clause_2:

        rule_81(clauses, expression_3)

    for clauses in renew_clause_2:
        renew_clause_3.append(clauses.subs(expression_3).expand())
    renew_clause_3

    expression_4 = {}
    renew_clause_4 = []
    for clauses in renew_clause_3:

        rule_81(clauses, expression_4)

    for clauses in renew_clause_3:
        renew_clause_4.append(clauses.subs(expression_4).expand())
    renew_clause_4

    expression_5 = {}
    renew_clause_5 = []
    for clauses in renew_clause_4:

        rule_11(clauses, expression_5)

    for clauses in renew_clause_4:
        renew_clause_5.append(clauses.subs(expression_5).expand())
    renew_clause_5

    expression_6 = {}
    renew_clause_6 = []
    for clauses in renew_clause_5:

        rule_11(clauses, expression_6)

    for clauses in renew_clause_5:
        renew_clause_6.append(clauses.subs(expression_6).expand())
    renew_clause_6

    expression_overall = {}
    expression_7 = {}
    renew_clause_7 = []
    for clauses in renew_clause_6:

        rule_21(clauses, expression_7)
        rule_21(clauses, expression_overall)
    print(expression_overall)

    for clauses in renew_clause_6:
        renew_clause_7.append(clauses.subs(expression_7).expand())
    renew_clause_7

    expression_8 = {}
    renew_clause_8 = []
    for clauses in renew_clause_7:

        rule_11(clauses, expression_8)

    for clauses in renew_clause_7:
        renew_clause_8.append(clauses.subs(expression_8).expand())
    renew_clause_8

    expression_9 = {}
    renew_clause_9 = []
    for clauses in renew_clause_8:

        rule_21(clauses, expression_9)
        rule_21(clauses, expression_overall)
    print(expression_overall)

    for clauses in renew_clause_8:
        renew_clause_9.append(clauses.subs(expression_9).expand())
    renew_clause_9

    expression_9 = {}
    renew_clause_91 = []
    for clauses in renew_clause_8:

        rule_21(clauses, expression_9)
        rule_21(clauses, expression_overall)
    print(expression_overall)

    for clauses in renew_clause_8:
        renew_clause_91.append(clauses.subs(expression_9).expand())
    renew_clause_91

    renew_clause_big = []
    expression_11 = {}
    """replace all the variable of equal with maximu with it's corresponding value"""
    for clauses in renew_clause_91:
        expression_10 = {}

        renew_clause_10 = []

        expression_10, p = rule_sum_equal(clauses, expression_10)

        if len(expression_10) != 0:

            for clauses in renew_clause_91:
                renew_clause_10.append(clauses.subs(expression_10).expand())
                for clauses in renew_clause_10:
                    if false_clause(clauses):
                        expression_11[p[0]] = 0

    for clauses in renew_clause_91:
        renew_clause_big.append(clauses.subs(expression_11).expand())

    renew_clause_big

    expression_12 = {}
    renew_clause_12 = []
    for clauses in renew_clause_big:

        rule77(clauses, expression_12)

    for clauses in renew_clause_big:
        renew_clause_12.append(clauses.subs(expression_12).expand())
    print(renew_clause_12)

    expression_13 = {}
    renew_clause_13 = []
    for clauses in renew_clause_12:

        rule_11(clauses, expression_12)

    for clauses in renew_clause_12:
        renew_clause_13.append(clauses.subs(expression_13).expand())
    print(renew_clause_13)

    print(expression_overall)

    expression_overall[Symbol("p3")] = Symbol("q3")
    expression_overall[Symbol("p5") + Symbol("q5")] = 1
    expression_overall[Symbol("p5") * Symbol("q5")] = 0
    print(expression_overall)
