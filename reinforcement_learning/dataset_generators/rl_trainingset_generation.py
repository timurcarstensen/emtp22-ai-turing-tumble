"""
This file is used to generate the training set / training samples for RL
"""

import os
from typing import Optional
import random
import time
from copy import deepcopy

# 3rd party imports
import pandas as pd
import numpy as np

# local imports (i.e. our own code)
# noinspection PyUnresolvedReferences
from utilities import utilities
from dataset_generators.utils import generate_control_flow_matrix_and_specification, get_outputs, \
    cf_to_lower_triangular_flattened, flattened_repr_to_control_flow_matrix


def generate_rl_training_set(
        size: Optional[int] = 100,
        n_bugs: Optional[int] = 5,
        sample_size: Optional[int] = 0,
        pickle: Optional[bool] = True
) -> pd.DataFrame:
    """
    Generates a training set for the RL algorithm

    :param pickle: whether to persist the training set as a pickle file
    :param size: of the training set
    :param n_bugs: number of bugs to be used
    :param sample_size: if 0: half of the specification size, else: sample_size number of specification pairs
    :return: pd.DataFrame(columns=["distance","input_samples", "output_samples", "modified_control_flow_matrix"])
    """
    training_set = pd.DataFrame(
        columns=[
            "distance",
            "input_samples",
            "output_samples",
            "modified_control_flow_matrix"
        ]
    )

    # time the training set generation and print the runtime
    start = time.time()

    # while the training set is not full
    while len(training_set) < size:
        # generate a random program and the full specification
        ins, outs, prog = generate_control_flow_matrix_and_specification(n_bugs=n_bugs)

        # if sample size not specified (i.e. 0), take exactly half of the full
        sample_size = int(((2 ** n_bugs) / 2) if sample_size == 0 else sample_size)

        # take a random subsample of the full specification
        sample_choice = random.sample(range(ins.shape[0]), sample_size)

        ins = ins[sample_choice, :]
        outs = outs[sample_choice, :]

        # convert the matrix to the vector representation
        flat_matrix = deepcopy(cf_to_lower_triangular_flattened(prog))
        subtractive_modifications = []
        queue = [(0, flat_matrix)]

        # generate subtractive modifications
        while queue:
            distance, current_element = queue.pop()
            edge_indices = np.argwhere(current_element == 1)
            local_results = []

            for index in edge_indices:
                tmp = deepcopy(current_element)
                tmp[index] = 0
                local_results.append(tmp)

            for modification in local_results:
                if subtractive_modifications:
                    appears = False
                    # check if the modification is already in the list
                    for _, elem in subtractive_modifications:
                        if np.array_equal(modification, elem):
                            appears = True
                    # if it is not in the list, add it to the queue and the list
                    if not appears:
                        queue.append((distance + 1, modification))
                        subtractive_modifications.append((distance + 1, modification))
                else:
                    queue.append((distance + 1, modification))
                    subtractive_modifications.append((distance + 1, modification))

        # generate additive modifications based on subtractive_modifications
        additive_modifications = []

        for distance, matrix in subtractive_modifications:
            # take random zero index and add one to it
            zero_indices = np.argwhere(matrix == 0)

            local_results = []

            for index in zero_indices:
                tmp = deepcopy(matrix)
                tmp[index] = 1
                local_results.append(tmp)

            # check that the additive modifications are not in additive_modifications or subtractive_modifications
            for modification in local_results:
                appears = False
                for _, elem in additive_modifications:
                    if np.array_equal(modification, elem):
                        appears = True
                if not appears:
                    for _, elem in subtractive_modifications:
                        if np.array_equal(modification, elem):
                            appears = True
                if not appears and not np.array_equal(modification, flat_matrix):
                    additive_modifications.append((distance + 1, modification))

        # generate additive modifications based on the original program
        flat_matrix = deepcopy(cf_to_lower_triangular_flattened(prog))
        original_additive_modifications = []
        queue = [(0, flat_matrix)]

        while queue and len(original_additive_modifications) < 30:
            distance, current_element = queue.pop()
            no_edge_indices = np.argwhere(current_element == 0)
            local_results = []

            for index in no_edge_indices:
                tmp = deepcopy(current_element)
                tmp[index] = 1
                local_results.append(tmp)

            for modification in local_results:

                appears = False
                # check if the modification is already in the list
                for _, elem in original_additive_modifications:
                    if np.array_equal(modification, elem):
                        appears = True
                # check if it is already in the additive_modifications list
                if not appears:
                    for _, elem in additive_modifications:
                        if np.array_equal(modification, elem):
                            appears = True

                # if it is not in the list, add it to the queue and the list
                if not appears:
                    queue.append((distance + 1, modification))
                    original_additive_modifications.append((distance + 1, modification))

        # merge subtractive_modifications, additive_modifications, original_additive_modifications into one list
        modifications = subtractive_modifications + additive_modifications + original_additive_modifications
        results = []

        # check if the modifications generate the same outputs as the original
        # program for the sample of the specification
        for distance, elem in modifications:
            mod_outs = get_outputs(
                n_bugs=n_bugs,
                ins=ins,
                prog=flattened_repr_to_control_flow_matrix(
                    flat_cf_repr=elem,
                    n_bugs=n_bugs)
            )
            # check if mod_outs and outs are the same
            if not np.array_equal(a1=outs, a2=mod_outs):
                results.append((distance, elem))

        # add the results that do not generate the same outputs as the original program to the training set
        for distance, elem in results:
            training_set = training_set.append(pd.DataFrame({
                "distance": distance,
                "input_samples": [ins],
                "output_samples": [outs],
                "modified_control_flow_matrix": [elem]
            }), ignore_index=True)

    end = time.time()
    print("RL training set generation took {} seconds".format(end - start))
    if pickle:
        training_set.to_pickle(
            f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/data/training_sets/rl_training_sets/rl_training_set_"
            f"{size}_{n_bugs}_{sample_size}.pkl"
        )
    return training_set


if __name__ == "__main__":
    random.seed(10)
    generate_rl_training_set(size=10000, n_bugs=3)
