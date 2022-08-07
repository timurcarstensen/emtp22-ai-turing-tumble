"""
This file contains relevant functions to create a dataset for pretraining the Reinforcement Learning Agent.
"""

# standard library imports
from typing import Tuple, Optional
from copy import deepcopy
import random
import pickle
from itertools import chain, combinations
import warnings
import os

# 3rd party imports
import numpy as np
from tqdm import tqdm

# local imports (i.e. our own code)
# noinspection PyUnresolvedReferences
from utilities import utilities
from dataset_generators.utils import generate_control_flow_matrix_and_specification, cf_to_lower_triangular_flattened


def solver(inputs: np.ndarray, outputs: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates a control flow matrix and the steps the solver takes for a given set of inputs and outputs

    :param inputs: list of specification inputs
    :param outputs: list of specification outputs
    :return: control flow matrix, solver steps
    """

    bits = len(inputs[0])

    cf_matrix = np.zeros(shape=(bits, 2 * bits), dtype=np.int64)

    algorithm_steps = []

    # the algorithm:
    for i, input_spec in enumerate(inputs):
        for j, input_elem in enumerate(input_spec[:-1]):
            if input_elem - outputs[i][j] != 0:
                for k, spec_elem in enumerate(input_spec):
                    if spec_elem - outputs[i][k] != 0 and k > j:
                        cf_matrix[k, 2 * j + 1 - input_spec[j]] = 1
                        if [k, 2 * j + 1 - input_spec[j]] not in algorithm_steps:
                            algorithm_steps.append([k, 2 * j + 1 - input_spec[j]])
                        break

    return cf_matrix, np.array(algorithm_steps)


def generate_sample(
        n_bugs: Optional[int] = 5,
        multiple_actions=False,
        reduced_modification_percentage: float = 0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list]:
    """
    Generates training samples for a given number of bugs. All training samples have the same input-output
    pairs but different control flow matrix modifications. It then returns the generated program (target)
    by the solver, the order of steps to create this program by the algorithm, the input output pairs
    and all the control flow matrix modifications.

    :param n_bugs: number of bugs
    :param multiple_actions: if True, the algorithm can take one of multiple delete actions in a single step.
    :param reduced_modification_percentage: percentage of unused control flow matrix modifications.
    If 0, all possible modifications are returned.

    :return: target program, algorithm steps, input output pairs, control flow matrix modifications
    """
    ins: np.ndarray
    outs: np.ndarray
    prog: np.ndarray
    ins, outs, prog = generate_control_flow_matrix_and_specification(n_bugs=n_bugs)

    # choose subset (half) of all input-output pairs
    choice = random.sample(range(ins.shape[0]), len(ins) // 2)
    ins = ins[choice, :]
    outs = outs[choice, :]

    algorithm_steps: np.ndarray
    prog, algorithm_steps = solver(inputs=ins, outputs=outs)

    # detect all partial solutions where at least one 1 has to be added
    s = list(np.argwhere(prog))
    powerset = chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

    res = []

    for _, elem in enumerate(powerset):
        a = np.zeros(shape=np.shape(prog), dtype=np.int64)
        for _, index in enumerate(elem):
            a[index[0], index[1]] = 1
        res.append(a)

    # remove as many modifications as specified by the percentage
    if reduced_modification_percentage > 0:
        idx_list = random.sample(range(0, len(res)),
                                 int(len(res) * reduced_modification_percentage)
                                 )  # remove 95% of samples for each function
        res_b = [elem for index, elem in enumerate(res) if index not in idx_list]
        res = res_b

    # create modifications where at least one 1 is added randomly to the respective CF matrix
    modifications = additive_modifications(np.array(res), prog=prog, multiple_actions=multiple_actions)
    return prog, algorithm_steps, ins, outs, modifications


def create_training_samples(n_bugs: int, multiple_actions: Optional[bool] = False,
                            reduced_modification_percentage: Optional[float] = 0.0):
    """
    Generates training samples for a given number of bugs. All training samples have the same input-output
    pairs but different control flow matrices. For each training sample, it creates a target probability
    vector, depending on which action to take next when following the expert algorithm. The probability
    vector is different, depending on whether an edge has to be added or deleted next.
    For each sample, it also returns the corresponding target matrix by the solver.

    :param n_bugs: number of bugs
    :param multiple_actions: if True, the algorithm can take one of multiple delete actions in a single step.
    :param reduced_modification_percentage: percentage of unused control flow matrix modifications.
    :return: x_samples, y_samples, sample_types, target program
    """

    x_samples = []
    y_samples = []
    sample_types = []
    ts = []

    # generate training samples for one input-output pair
    t, algorithm_steps, ins, outs, modifications = generate_sample(
        n_bugs=n_bugs,
        multiple_actions=multiple_actions,
        reduced_modification_percentage=reduced_modification_percentage
    )

    # create label vectors for each training sample
    for pre in modifications:
        label = np.zeros(((n_bugs * 2 * n_bugs) // 2 - n_bugs,))

        diff: np.array = t - pre

        # Check
        if -1 in diff:
            indices = np.argwhere(diff == -1)
            # how many Ones could we remove
            ahead = len(indices)
            for index in indices:
                # equally distribute the probability mass over all possible deletions
                label[get_new_index(n_bugs, index)] = 1 / ahead
            sample_type = -1
        elif 1 in diff:
            indices = np.argwhere(diff == 1)
            sample_type = 1
            set_one = False
            for coord in algorithm_steps:
                for ind in indices:
                    if np.array_equal(coord, ind):
                        # put all weight on next add action of solving algorithm
                        label[get_new_index(n_bugs, coord)] = 1
                        set_one = True
                        break
                if set_one:
                    break
        else:
            raise AssertionError("Pre Matrix equals target Matrix")

        pre1 = cf_to_lower_triangular_flattened(cf_matrix=pre)

        ins1 = np.array(ins).flatten()
        outs1 = np.array(outs).flatten()
        x1 = np.concatenate((pre1, ins1, outs1))
        label = label.flatten()
        x_samples.append(x1)
        y_samples.append(label)
        sample_types.append(sample_type)
        ts.append(t)
    return x_samples, y_samples, sample_types, ts


def additive_modifications(
        history: np.ndarray,
        n_modifications: Optional[int] = 1,
        multiple_actions: Optional[bool] = False,
        prog=None
) -> list:
    """
    Returns additive modifications of the history created by the solving algorithm

    :param prog: The target CF matrix found by the algorithm
    :param history: in-template history
    :param n_modifications: how many modifications to produce for each history element
    :param multiple_actions: whether we want to produce training samples, where more than one action is needed to
    get back on template or not
    :return: array of arrays of original history elements and their additive modifications. The originals
    are the 0th elements in each array
    """

    warnings.warn(
        message="additive_modifications() (so far) does not check whether "
                "a generated additive modification leads to a on sample matrix",
        category=FutureWarning,
        stacklevel=1)

    res: list = []

    possible_coordinate_mappings = get_valid_coordinates(n_bugs=len(history[0]))

    for _, hist_elem in enumerate(history):
        if not np.array_equal(prog, hist_elem):
            res.append(hist_elem)
        for n in range(n_modifications):
            tmp = deepcopy(hist_elem)
            z = 1
            if multiple_actions:
                # Flip up to 3 bits in the CF matrix depending on the given probabilities
                z = np.random.choice([1, 2, 3], 1, p=[0.5, 0.3, 0.2])[0]
            for _ in range(z):
                idx = np.random.choice(len(possible_coordinate_mappings))
                tmp[possible_coordinate_mappings[idx]] = 1
            if not np.array_equal(prog, tmp):
                res.append(tmp)

    return res


def get_new_index(n_bugs: int, coordinate: Tuple[int, int]) -> int:
    """
    Gets a coordinate of a CF matrix entry and return its corresponding index in the target label, if
    the control flow matrix is a lower triangle matrix (waterfall principle).

    :param n_bugs: Number of Bugs
    :param coordinate: A coordinate (x,y) of a matrix
    :return: int: Element index if relevant CF matrix entries are sorted line by line
    """

    c_normal = coordinate[0] * 2 * n_bugs + coordinate[1]
    new_index = c_normal
    for i in range(coordinate[0]):
        new_index = new_index - (2 * n_bugs - 2 * i)
    return new_index


def get_valid_coordinates(n_bugs: int) -> dict:
    """
    Returns a dict that maps the new index of a coordinate in the lower triangle matrix

    to the original coordinate
    :param n_bugs: Number of Bugs
    :return: dict: Maps the new index of a coordinate in the lower triangle matrix to a valid x,y coordinate pair
    """

    # a dict containing sorted relevant CF coordinates
    transformations = dict()
    for i in range(n_bugs):
        for j in range(2 * n_bugs):
            if j >= 2 * i:
                continue
            transformations[get_new_index(n_bugs, (i, j))] = (i, j)
    return transformations


def write_samples_to_file(
        num_bugs: int,
        x_samples: np.ndarray,
        y_samples: np.ndarray,
        sample_types: np.ndarray,
        programs: np.ndarray,
        multiple_actions: Optional[bool] = False,
        verbose: Optional[bool] = False
):
    """
    Writes samples to file. The samples are written to a file in the following format:

    :param num_bugs: Number of Bugs
    :param x_samples: Training Samples (CF Matrix, Inputs, Outputs respectively)
    :param y_samples: Target Labels
    :param sample_types: Sample Types
    :param programs: Programs
    :param multiple_actions: Whether we want to produce training samples, where more than one delete action is possible
    :param verbose: Whether we want to print the progress of the writing process
    :return: None
    """
    file_path = f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/data/training_sets/pretraining_training_sets"
    x_file_name = f"{file_path}/X_TrainingSet{num_bugs}{('multiple_actions' if multiple_actions else '')}.pkl"
    y_file_name = f"{file_path}/Y_TrainingSet{num_bugs}{('multiple_actions' if multiple_actions else '')}.pkl"
    type_file_name = f"{file_path}/SampleTypes{num_bugs}{('multiple_actions' if multiple_actions else '')}.pkl"
    program_file_name = f"{file_path}/Programs{num_bugs}{('multiple_actions' if multiple_actions else '')}.pkl"

    for file, samples in [
        (x_file_name, x_samples),
        (y_file_name, y_samples),
        (type_file_name, sample_types),
        (program_file_name, programs)
    ]:
        with open(file, 'wb') as f:
            pickle.dump(samples, f, protocol=pickle.HIGHEST_PROTOCOL)

    if verbose:
        print("\nWrote ", len(x_samples), "training samples to Files.")

        values, counts = np.unique(sample_types, return_counts=True)
        type0 = "REMOVE_EDGES" if values[0] == -1 else "ADD_EDGES"
        type1 = "ADD_EDGES" if type0 == "REMOVE_EDGES" else "REMOVE_EDGES"
        print(f"{counts[0]} ({round((counts[0] / len(x_samples)) * 100, 2)}%) samples are of type '{type0}'.")
        print(f"{counts[1]} ({round((counts[1] / len(x_samples)) * 100, 2)}%) samples are of type '{type1}'.")


def read_samples(
        num_bugs: int,
        multiple_actions: Optional[bool] = False,
        verbose: Optional[bool] = False
):
    """
    Reads x,y samples from file. The samples are read from a file in the following format:

    :param num_bugs: Number of Bugs
    :param multiple_actions: Whether we want to use training samples, where more than one delete action is possible
    :param verbose: Whether we want to print the progress of the reading process
    :return: None
    """

    file_path = f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/data/training_sets/pretraining_training_sets"
    x_file_name = f"{file_path}/X_TrainingSet{num_bugs}{('multiple_actions' if multiple_actions else '')}.pkl"
    y_file_name = f"{file_path}/Y_TrainingSet{num_bugs}{('multiple_actions' if multiple_actions else '')}.pkl"

    with open(x_file_name, 'rb') as f:
        x_samples = pickle.load(f)

    with open(y_file_name, 'rb') as f:
        y_samples = pickle.load(f)

    if verbose:
        print("\nRead ", len(x_samples), "training samples from Files.")
    return x_samples, y_samples


def read_sample_types(
        num_bugs: int,
        multiple_actions: Optional[bool] = False,
        verbose: Optional[bool] = False
):
    """
    Reads the sample types from the given file. A sample type can be either -1 or 1. -1 means that this sample is
    a sample, where the corresponding PRE matrix has at least one 1 too much. 1 means that the PRE matrix does
    not have unnecessary/wrong ones, but at least one 1 has to be added.

    :param num_bugs: Number of Bugs
    :param multiple_actions: Whether we want to use training samples, where more than one delete action is possible.
    :param verbose: Whether we want to print the progress of the reading process
    :return: Sample Types
    """

    file_path = f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/data/training_sets/pretraining_training_sets"
    type_file_name = f"{file_path}/SampleTypes{num_bugs}{('multiple_actions' if multiple_actions else '')}.pkl"

    with open(type_file_name, "rb") as f:
        sample_types = pickle.load(f)

    if verbose:
        print("\nRead Sample Types.")
        values, counts = np.unique(sample_types, return_counts=True)
        type0 = "REMOVE_EDGES" if values[0] == -1 else "ADD_EDGES"
        type1 = "ADD_EDGES" if type0 == "REMOVE_EDGES" else "REMOVE_EDGES"
        print(f"{counts[0]} ({round((counts[0] / len(sample_types)) * 100, 2)}%) samples are of type '{type0}'.")
        print(f"{counts[1]} ({round((counts[1] / len(sample_types)) * 100, 2)}%) samples are of type '{type1}'.")

    return sample_types


def read_programs(
        num_bugs: int,
        multiple_actions: Optional[bool] = False,
        verbose: Optional[bool] = False
):
    """
    Reads the programs from the given file. A Program is the target matrix for the corresponding input output pairs
    found by the algorithm.

    :param num_bugs: Number of Bugs
    :param multiple_actions: Whether we want to use training samples, where more than one delete action is possible.
    :param verbose: Whether we want to print the progress of the reading process
    :return: Programs
    """
    file_path = f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/data/training_sets/pretraining_training_sets"
    type_file_name = f"{file_path}/Programs{num_bugs}{('multiple_actions' if multiple_actions else '')}.pkl"

    with open(type_file_name, "rb") as f:
        programs = pickle.load(f)

    if verbose:
        print(f"\nRead {len(programs)} Programs.")

    return programs


def create_pretraining_dataset(
        num_bugs: int,
        multiple_actions: Optional[bool] = False,
        reduced_modification_percentage: Optional[float] = 0.0,
        upper_bound_size: Optional[int] = 500000,
        verbose: Optional[bool] = False
):
    """
    Creates a full pretraining dataset for pretraining the Reinforcement Learning Agent.
    The dataset consists of training samples, of which each has a control flow matrix and input-output pairs.
    Pretraining is done in a supervised way with label vectors determining the desired action the agent should take.

    :param num_bugs: Number of Bugs
    :param multiple_actions: Whether we want to use training samples, where more than one delete action is possible.
    :param reduced_modification_percentage: Percentage of samples, which are randomly removed from the dataset. If the
    value is high, this increases the number of different input-output pairs in the dataset.
    :param upper_bound_size: Maximum size of the dataset.
    :param verbose: Whether we want to print the progress of the creation process.
    :return: None
    """

    x_samples = []
    y_samples = []
    sample_types = []
    programs = []
    for i in tqdm(range(200000)):
        x_sample, y_sample, sample_type, t = create_training_samples(
            n_bugs=num_bugs,
            multiple_actions=multiple_actions,
            reduced_modification_percentage=reduced_modification_percentage
        )

        x_samples += x_sample
        y_samples += y_sample
        sample_types += sample_type
        programs += t

        if len(x_samples) > upper_bound_size:
            print("Specifications tried: ", i)
            print("Samples: ", len(x_samples))
            break

    x_samples = np.array(x_samples, dtype=float)
    y_samples = np.array(y_samples, dtype=float)

    print("Complete Size in Bytes: ", x_samples.size * x_samples.itemsize)

    # we don't want duplicates in our training set
    x_samples, lbl_indices = np.unique(x_samples, return_index=True, axis=0)
    y_samples = np.take(y_samples, lbl_indices, axis=0)
    sample_types = np.take(sample_types, lbl_indices, axis=0)
    all_programs = np.take(programs, lbl_indices, axis=0)
    print("Size after removing Duplicates: ", len(x_samples))

    # how many functions do we have?
    number_of_functions = np.unique(x_samples[:, num_bugs * (num_bugs - 1):], return_index=False, axis=0)
    print("Number of Functions: ", len(number_of_functions))

    # write Training set into files
    write_samples_to_file(
        num_bugs=num_bugs,
        x_samples=x_samples,
        y_samples=y_samples,
        sample_types=sample_types,
        programs=all_programs,
        multiple_actions=multiple_actions,
        verbose=verbose
    )


if __name__ == "__main__":
    random.seed(10)
    create_pretraining_dataset(
        num_bugs=3,
        multiple_actions=True,
        reduced_modification_percentage=0.95,
        upper_bound_size=10000,
        verbose=True
    )
