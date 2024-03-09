import pandas as pd

# from qiskit import Aer, transpile
from tabulate import tabulate


def get_tuples(x_list, y_list):
    if len(x_list) != len(y_list):
        raise ValueError("The two lists must have the same length.")

    return set(zip(x_list, y_list))


def keep_max_y_coordinate(tuples_set):
    # Create a dictionary to store the maximum y coordinate for each x coordinate
    max_y_coordinates = {}

    for x, y in tuples_set:
        if x in max_y_coordinates:
            max_y_coordinates[x] = max(max_y_coordinates[x], y)
        else:
            max_y_coordinates[x] = y

    # Create a new set with the tuples having maximum y coordinate for each x coordinate
    result_set = {(x, y) for x, y in tuples_set if y == max_y_coordinates[x]}

    return result_set


def statevector(qc):
    simulator = Aer.get_backend("statevector_simulator")
    result = simulator.run(transpile(qc, simulator)).result()
    return result.get_statevector()


def get_table_bin_combinations(table):
    # Create a copy of the input table
    new_table = table.copy()

    def concat_binary_values(row):
        # Convert the binary values to strings and concatenate them
        return "".join(str(val) for val in row)

    # Create a new column 'concatenated_binary' in the new table to store the results
    new_table["concatenated_binary"] = new_table.apply(concat_binary_values, axis=1)

    # Convert the 'concatenated_binary' column to a list
    binary_list = new_table["concatenated_binary"].tolist()

    return binary_list


def convert_elements_to_str(input_set):
    output_set = set()

    for element in input_set:
        output_set.add(str(element))

    return output_set


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
