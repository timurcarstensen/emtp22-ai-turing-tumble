"""
This file contains useful functions to create the datasets for pretraining as well as for the reinforcement learning.
"""
# standard library imports
from typing import List, Tuple, Optional

from numpy import binary_repr
import numpy as np
# noinspection PyPackageRequirements
import jpype
# noinspection PyUnresolvedReferences
from utilities import utilities

CF_Translated = jpype.JClass(
    "de.bugplus.examples.development.CF_Translated"
)


def generate_control_flow_matrix_and_specification(n_bugs: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generates a control flow matrix and the corresponding specification

    :param n_bugs: number of bugs
    :return:
    """

    prog = generate_control_flow_sequentially(n_bugs=n_bugs)

    ins: np.ndarray = generate_ins(n_bugs=n_bugs)
    outs = []

    for _, elem in enumerate(ins):
        outs.append(np.array(CF_Translated.execute(n_bugs, prog, elem), dtype=np.int64))
    return ins, np.array(outs), prog


def get_outputs(n_bugs: int, ins: np.ndarray, prog: np.ndarray) -> List[np.ndarray]:
    """
    For a given input and program, returns the outputs of the program

    :param n_bugs: number of bugs of the program
    :param ins: program inputs
    :param prog: control flow matrix of the program
    :return: program outputs of len(ins)
    """
    outs = []
    for _, elem in enumerate(ins):
        outs.append(np.array(CF_Translated.execute(n_bugs, prog, elem), dtype=np.int64))
    return outs


def generate_ins(n_bugs: int) -> np.ndarray:
    """
    Generates all possible inputs for the generator for a given number of bugs

    :param n_bugs: number of bugs the program will have
    :return: ndarray of all possible inputs
    """
    return np.array(
        [
            np.array([int(bit) for bit in binary_repr(num=n, width=n_bugs)], dtype=np.int64)
            for n in range(2 ** n_bugs)
        ]
    )


def generate_control_flow_sequentially(n_bugs: int, num_edges: Optional[int] = None) -> np.ndarray:
    """
    returns a (sequentially) generated control flow matrix for turing tumble / BugBit

    :param n_bugs: number of bugs used
    :param num_edges: number of edges to be used (OPTIONAL)
    :return: generated control flow matrix (NDArray)
    """
    connected_bugs = [0]

    cf = np.zeros(shape=(2 * n_bugs, n_bugs), dtype=np.int64)

    sink = -3

    num_edges = 2 * (n_bugs - 1) if not num_edges else num_edges

    while connected_bugs and num_edges != 0:
        current_bug = connected_bugs[0]

        options = list(range(current_bug + 1, n_bugs)) + [sink]

        choice_a, choice_b = np.random.choice(a=options, size=2)

        if choice_a != sink:
            cf[current_bug * 2, choice_a] = 1
            num_edges -= 1
            if choice_a not in connected_bugs:
                connected_bugs.append(choice_a)

        if choice_b != sink and num_edges != 0:
            cf[current_bug * 2 + 1, choice_b] = 1
            num_edges -= 1
            if choice_b not in connected_bugs:
                connected_bugs.append(choice_b)

        connected_bugs.remove(current_bug)

    return cf.T


def flattened_repr_to_control_flow_matrix(flat_cf_repr: np.ndarray, n_bugs: int) -> np.ndarray:
    """
    Converts a flattened representation of the control flow matrix to a control flow matrix

    :param flat_cf_repr:
    :param n_bugs:
    :return:
    """
    cf_new = np.zeros(shape=(n_bugs, 2 * n_bugs), dtype=np.int64)

    i = 0
    for rowindex in range(n_bugs):
        # remove the irrelevant CF Matrix elements (waterflow principle, upper right corner)
        row_add_indices = list(range(2 * rowindex))

        for rai in row_add_indices:
            # print(rowindex, rai, i)
            cf_new[rowindex, rai] = flat_cf_repr[i]
            i += 1
    return cf_new


def cf_to_lower_triangular_flattened(cf_matrix: np.ndarray) -> np.ndarray:
    """
    Converts a control flow matrix to a lower triangular matrix represented as a vector

    :param cf_matrix:
    :return:
    """
    n_bugs = len(cf_matrix)

    remove_indices = []

    for rowindex in range(len(cf_matrix)):
        row_remove_indices = list(range(2 * rowindex + rowindex * 2 * n_bugs, 2 * n_bugs * (rowindex + 1)))
        remove_indices += row_remove_indices

    cf_matrix = np.array(cf_matrix).flatten()

    return np.delete(cf_matrix, remove_indices)
