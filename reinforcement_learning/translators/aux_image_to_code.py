"""
This file contains the translator (T2) from a matrix representation of a Turing Tumble Board (as can be obtained from
the Turing Tumble Simulator as a png image) to BugBit code that is executed via jpype.

"""

# standard library imports
import os
from typing import List
import json
import pickle

# 3rd party imports
# noinspection PyPackageRequirements
import jpype
import numpy as np

# local imports
# noinspection PyUnresolvedReferences
from utilities import utilities

# get java classes
NegBugsBasicArithmetic = jpype.JClass(
    "de.bugplus.examples.development.NegBugsBasicArithmetic"
)
BugplusLibrary = jpype.JClass("de.bugplus.specification.BugplusLibrary")
BugplusProgramSpecification = jpype.JClass(
    "de.bugplus.specification.BugplusProgramSpecification"
)
BugplusProgramImplementation = jpype.JClass(
    "de.bugplus.development.BugplusProgramImplementation"
)
BugplusProgramInstanceImpl = jpype.JClass(
    "de.bugplus.development.BugplusProgramInstanceImpl"
)
BugplusThread = jpype.JClass("de.bugplus.development.BugplusThread")
BugplusDevelopment = jpype.JPackage("de.bugplus.development")

logfile = open('logfile.txt', "w")


class Translator:
    # The identifying number for each piece and field
    _left_edge_rep: int = 1
    _right_edge_rep: int = 2
    _bidir_edge_rep: int = 3
    _gear_rep: int = 4
    _zero_bit_rep: int = 5
    _stopping_pin_rep: int = 6
    _zero_gearbit_rep: int = 7
    _one_gearbit_rep: int = 8
    _one_bit_rep: int = 9

    # fields
    _invalid_field: int = -100

    # board size
    _board_shape: tuple = (11, 11)

    # other class variables
    matrix: np.ndarray = np.zeros(shape=_board_shape)
    function_library: None = None
    bug_counter: int = 0
    specification: BugplusProgramSpecification = None
    challenge_implementation: BugplusProgramImplementation = None
    bug_matrix: np.array = np.zeros(shape=_board_shape, dtype=object)
    file_write: bool = False

    bugplus_development_path: str = f"{os.getenv('REINFORCEMENT_LEARNING_DIR')}/../src/de/bugplus/examples/development/"

    # for the translation into a simple CF-Matrix
    num_bugs: int = 0

    def matrix_to_bugbit_code(self, mtrx: str):
        """
        Takes a matrix representing the board and turns it into executable BugBit code

        :param mtrx: A representation of a Turing Tumble board
        :return: None
        """
        # decode the matrix
        mtrx = json.loads(mtrx)
        mtrx = np.array(mtrx["array"])

        # the blueprint of the java file that can run a BugPlus program is copied into the Challenge.java file
        with open(self.bugplus_development_path + "Blueprint.txt", "r") as template:
            blueprint = template.readlines()
            with open(
                    self.bugplus_development_path + "Challenge.java", "w"
            ) as challenge:
                for b in blueprint:
                    challenge.write(b)
        # run the blueprint in python via JPype
        self.matrix: np.array = mtrx
        # self.write_to_file(f"Matrix: {self.matrix}")
        self.function_library = BugplusLibrary.getInstance()
        negation_bug_implementation = (
            BugplusDevelopment.BugplusNEGImplementation.getInstance()
        )
        self.function_library.addSpecification(
            negation_bug_implementation.getSpecification()
        )

        self.specification = BugplusProgramSpecification.getInstance(
            "T2_Code", 0, 2, self.function_library
        )

        # additionally, write to file
        self.write_to_file(
            'BugplusProgramSpecification T2_Code_specification = BugplusProgramSpecification.getInstance'
            '("T2_Code_Instance", 0, 2, myFunctionLibrary); '
        )

        self.challenge_implementation = self.specification.addImplementation()
        self.write_to_file(
            "BugplusProgramImplementation T2_Code_Implementation = T2_Code_specification.addImplementation();"
        )
        # add a negation bug for each bit on the board
        for i in self.find_bits():
            self.bug_matrix[i[0], i[1]] = self.addNegBug()
            self.num_bugs += 1

        # create CF Matrix:
        self.cf_matrix = np.zeros(shape=(self.num_bugs, 2 * self.num_bugs), dtype=np.int)

        # connect the control in flow of the framework program to the first bit that will be active when starting a game
        try:
            self.connect_starting_bit()
        except Exception:
            self.write_to_file("An error happened when connecting the ControlInInterface")

        # control flow: connect the bugs with each other
        try:
            self.connect_bits()
        except Exception:
            self.write_to_file("Bug in Connect Blue bits")

        # data flow: connect the bugs with each other
        try:
            self.synchronize_connected_gear_bits()
        except Exception as e:
            self.write_to_file("Bug in Connect Coherent Components")
            self.write_to_file(str(e))

        # implement an instance of our BugPlus program
        challenge_instance = self.challenge_implementation.instantiate()
        self.write_to_file(
            "BugplusInstance challengeInstance = T2_Code_Implementation.instantiate();"
        )

        t2_code_instance_impl = challenge_instance.getInstanceImpl()
        self.write_to_file(
            "BugplusProgramInstanceImpl T2_Code_Instance_Impl = challengeInstance.getInstanceImpl();"
        )

        # flip each bit corresponding to its starting state
        bug_pos = self.find_bits()
        for pos in bug_pos:
            id = self.bug_matrix[pos]
            value = 0

            if self.matrix[pos] in [self._one_bit_rep, self._one_gearbit_rep]:
                value = 1
            t2_code_instance_impl.getBugs().get(id).setInternalState(value)
            self.write_to_file(
                f'T2_Code_Instance_Impl.getBugs().get("{id}").setInternalState({value});'
            )

        # create a thread that can run the program via JPype
        new_thread = BugplusThread.getInstance()
        self.write_to_file("BugplusThread newThread = BugplusThread.getInstance();")
        new_thread.connectInstance(challenge_instance)
        self.write_to_file("newThread.connectInstance(challengeInstance);")

        # run the program via JPype
        self.write_to_file("newThread.start();")

        # print information regarding the bits' states and call counters
        ids = []
        for pos in bug_pos:
            ids.append(self.bug_matrix[pos])

        self.write_to_file(
            "LinkedList<String> challengeBugs = new LinkedList<String>();"
        )

        for id in ids:
            print(
                f"Internal State: {id} : \t {t2_code_instance_impl.getBugs().get(id).getInternalState()}"
            )
            print(
                f"Call Counter: {id} : \t {t2_code_instance_impl.getBugs().get(id).getCallCounter()}"
            )

            self.write_to_file(
                f'System.out.println("Internal State " + "{id}" + ": \t" + T2_Code_Instance_Impl.getBugs().get("{id}")'
                f'.getInternalState());'
            )
            self.write_to_file(
                f'System.out.println("Call Counter " + "{id}" + ": \t" + T2_Code_Instance_Impl.getBugs().get("{id}")'
                f'.getCallCounter() + "\\n");'
            )

        with open('CF_Matrix.pkl', 'wb') as handle:
            pickle.dump(self.cf_matrix, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def connect_bits(self):
        """
        Connects the control flow of the bits.

        :return: None
        """

        # get all positions with bits
        bit_positions = self.find_bits()

        # using 2 individual buckets (one red one blue)
        # blue_bucket_out = (0, int((self._BOARD_SHAPE[1] + 1) / 4))
        # red_bucket_out = (0, int(self._BOARD_SHAPE[1] - (self._BOARD_SHAPE[1] + 1) / 4 - 1))

        # using 1 single shared bucket in the top center of the board
        blue_bucket_out = (0, int(self._board_shape[1] / 2))
        red_bucket_out = blue_bucket_out

        # for each bit
        for current_pos in bit_positions:

            # the current momentum
            momentum_right_next_l = False
            momentum_right_next_r = True

            # assign coordinates for bottom left and bottom right of bit
            next_l = (current_pos[0] + 1, current_pos[1] - 1)
            next_r = (current_pos[0] + 1, current_pos[1] + 1)

            # check if next position is out of bounds
            if next_l[1] < 0 or next_l[1] > self._board_shape[1] - 1:
                next_l = None
            if next_r[1] < 0 or next_r[1] > self._board_shape[1] - 1:
                next_r = None
            if self.matrix[next_l[0], next_l[1]] == -100:
                next_l = None
            if self.matrix[next_r[0], next_r[1]] == -100:
                next_r = None

            # all bits that will be implemented as bugs
            mask_list = [
                self._one_bit_rep,
                self._zero_bit_rep,
                self._one_gearbit_rep,
                self._zero_gearbit_rep,
                self._stopping_pin_rep,
            ]

            # exit bit to the left
            if next_l:
                # as long as we don't arrive at the next bit
                while self.matrix[next_l] not in mask_list:
                    # check if we are in second to last row
                    if next_l[0] == self._board_shape[0] - 2:
                        # specify which switch will be activated
                        if next_l[1] in [0, 2]:
                            next_l = blue_bucket_out
                            momentum_right_next_l = True
                            continue
                        elif next_l[1] in [6, 8]:
                            next_l = red_bucket_out
                            momentum_right_next_l = True
                            continue
                        elif (
                                next_l[1] == 4
                                and self.matrix[next_l] == self._left_edge_rep
                        ):
                            next_l = blue_bucket_out
                            momentum_right_next_l = True
                            continue
                        elif (
                                next_l[1] == 6
                                and self.matrix[next_l] == self._right_edge_rep
                        ):
                            next_l = red_bucket_out
                            momentum_right_next_l = True
                            continue

                    # check if we are in last row
                    elif next_l[0] == self._board_shape[0] - 1:
                        # assign which switch will be activated
                        if next_l[1] != 5:
                            next_l = None
                            raise AssertionError(
                                "This is an error. This coordinate should never appear (next_l)."
                            )

                        elif self.matrix[next_l] == self._left_edge_rep:
                            next_l = blue_bucket_out
                            momentum_right_next_l = True
                            continue
                        elif self.matrix[next_l] == self._right_edge_rep:
                            next_l = red_bucket_out
                            momentum_right_next_l = False
                            continue
                    # normal case: check what next edge will be
                    # green edges
                    if self.matrix[next_l] == self._right_edge_rep:
                        next_l = (next_l[0] + 1, next_l[1] + 1)
                        momentum_right_next_l = True
                    elif self.matrix[next_l] == self._left_edge_rep:
                        next_l = (next_l[0] + 1, next_l[1] - 1)
                        momentum_right_next_l = False
                    # orange bidirectional edge
                    elif self.matrix[next_l] == self._bidir_edge_rep:
                        if momentum_right_next_l:
                            next_l = (next_l[0] + 1, next_l[1] + 1)
                        else:
                            next_l = (next_l[0] + 1, next_l[1] - 1)
                    # check if next position will be out of bounds (if we follow edge)
                    if next_l[1] < 0 or next_l[1] > self._board_shape[1] - 1:
                        next_l = None
                        raise AssertionError(
                            "This is an error. Next next_l position is out of bounds."
                        )

                    if self.matrix[next_l[0], next_l[1]] == -100:
                        next_l = None
                        raise AssertionError(
                            "This is an error. Next next_l position is out of bounds."
                        )

                # we reached the next bit
                if next_l:

                    # assign ids of the bits to connect
                    id_1 = self.bug_matrix[current_pos]
                    id_2 = self.bug_matrix[next_l]

                    if type(id_2) != str:
                        self.challenge_implementation.connectControlOutInterface(id_1, 0, 0)
                        self.challenge_implementation.connectControlOutInterface(id_1, 0, 1)
                        self.write_to_file(
                            f'T2_Code_Implementation.connectControlOutInterface("{id_1}", 0, 0);'
                        )
                        self.write_to_file(
                            f'T2_Code_Implementation.connectControlOutInterface("{id_1}", 0, 1);'
                        )

                    else:
                        self.challenge_implementation.addControlFlow(id_1, 0, id_2)
                        self.write_to_file(
                            f'T2_Code_Implementation.addControlFlow("{id_1}", 0, "{id_2}");'
                        )

                        # reparse ids:
                        i1 = int(id_1.split("_")[1])
                        i2 = int(id_2.split("_")[1])

                        # set 1 in CF Matrix
                        self.cf_matrix[i2, 2 * i1] = 1

            # exit bit to the right
            if next_r:
                # as long as we don't arrive at the next bit
                while self.matrix[next_r] not in mask_list:
                    # specify which switch will be activated
                    if next_r[0] == self._board_shape[0] - 2:
                        if next_r[1] in [0, 2]:
                            next_r = blue_bucket_out
                            momentum_right_next_r = True
                            continue
                        elif next_r[1] in [6, 8]:
                            next_r = red_bucket_out
                            momentum_right_next_r = True
                            continue
                        elif (
                                next_r[1] == 4
                                and self.matrix[next_r] == self._left_edge_rep
                        ):
                            next_r = blue_bucket_out
                            momentum_right_next_r = True
                            continue
                        elif (
                                next_r[1] == 6
                                and self.matrix[next_r] == self._right_edge_rep
                        ):
                            next_r = red_bucket_out
                            momentum_right_next_r = True
                            continue

                    # check if we are in last row
                    elif next_r[0] == self._board_shape[0] - 1:
                        # assign which swith will be activated
                        if next_r[1] != 5:
                            next_r = None
                            raise AssertionError(
                                "This is an error. This coordinate should never appear (next_r)."
                            )
                        elif self.matrix[next_r] == self._left_edge_rep:
                            next_r = blue_bucket_out
                            momentum_right_next_r = True
                            continue
                        elif self.matrix[next_r] == self._right_edge_rep:
                            next_r = red_bucket_out
                            momentum_right_next_r = False
                            continue

                    # usual case: check what next edge will be
                    # green edges
                    elif self.matrix[next_r] == self._right_edge_rep:
                        next_r = (next_r[0] + 1, next_r[1] + 1)
                        momentum_right_next_r = True
                    elif self.matrix[next_r] == self._left_edge_rep:
                        next_r = (next_r[0] + 1, next_r[1] - 1)
                        momentum_right_next_r = False

                    # orange bidirectional edge
                    elif self.matrix[next_r] == self._bidir_edge_rep:
                        if momentum_right_next_r:
                            next_r = (next_r[0] + 1, next_r[1] + 1)
                        else:
                            next_r = (next_r[0] + 1, next_r[1] - 1)

                    # check if next position will be out of bounds (if we follow edge)
                    if next_r[1] < 0 or next_r[1] > self._board_shape[1] - 1:
                        next_r = None
                        raise AssertionError(
                            "This is an error. Next next_r position is out of bounds."
                        )
                    if self.matrix[next_r[0], next_r[1]] == -100:
                        next_r = None
                        raise AssertionError(
                            "This is an error. Next next_r position is out of bounds."
                        )

                # we reached the next bit
                if next_r:
                    id_1 = self.bug_matrix[current_pos]
                    id_2 = self.bug_matrix[next_r]
                    # assign ids of the bits to connect
                    if type(id_2) != str:
                        self.challenge_implementation.connectControlOutInterface(id_1, 1, 0)
                        self.challenge_implementation.connectControlOutInterface(id_1, 1, 1)
                        self.write_to_file(
                            f'T2_Code_Implementation.connectControlOutInterface("{id_1}", 1, 0);'
                        )
                        self.write_to_file(
                            f'T2_Code_Implementation.connectControlOutInterface("{id_1}", 1, 1);'
                        )
                    else:
                        self.challenge_implementation.addControlFlow(id_1, 1, id_2)
                        # self.addControlFlow(id_1, 1, id_2)
                        self.write_to_file(
                            f'T2_Code_Implementation.addControlFlow("{id_1}", 1, "{id_2}");'
                        )
                        # reparse ids:
                        i1 = int(id_1.split("_")[1])
                        i2 = int(id_2.split("_")[1])
                        # set 1 in CF Matrix
                        self.cf_matrix[i2, 2 * i1 + 1] = 1

    def connect_starting_bit(self):
        """
        Connects the initial control flow of the interface with the first bit

        :return: None
        """

        # define the position just below the blue bucket
        starting_pos = (0, int(self._board_shape[1] / 2))
        next_pos = starting_pos
        momentum_right = True

        # follow the edges until we encounter a bit
        while next_pos not in self.find_bits():

            # follow green edges
            if self.matrix[next_pos] == self._right_edge_rep:
                next_pos = (next_pos[0] + 1, next_pos[1] + 1)
                momentum_right = True
            elif self.matrix[next_pos] == self._left_edge_rep:
                next_pos = (next_pos[0] + 1, next_pos[1] - 1)
                momentum_right = False

            # follow orange edges
            elif self.matrix[next_pos] == self._bidir_edge_rep:
                if momentum_right:
                    next_pos = (next_pos[0] + 1, next_pos[1] + 1)
                else:
                    next_pos = (next_pos[0] + 1, next_pos[1] - 1)

        # connect the control flow of the interface with the bit that will be activated first when starting the program
        start_id = self.bug_matrix[next_pos]
        self.connectControlInInterface(start_id)

    def connect_gear_bits(self, gear_bit_pos: tuple) -> List[tuple]:
        """
        Identifies gear bits that are connected via gears

        :param gear_bit_pos: The position of a single gearbit on the board
        :return: a list of the gear bits that are connected via gears
        """

        # check for gears and gear bits directly connected with input gear bit
        connected_components = [gear_bit_pos]
        list_size_increase = True

        # as long as we keep finding neighbouring gears or gear bits
        while list_size_increase:
            list_size_increase = False

            # for all gears and gear bits already in the list
            for component in connected_components:

                # check in all four directions for neighboring gears or gearbits
                above_pos = (component[0] - 1, component[1])
                below_pos = (component[0] + 1, component[1])
                right_pos = (component[0], component[1] + 1)
                left_pos = (component[0], component[1] - 1)

                # if a gear or gear bit is found, add it to the list
                if self.check_gear_or_gearbit(above_pos):
                    if above_pos not in connected_components:
                        connected_components.append(above_pos)
                        list_size_increase = True

                if self.check_gear_or_gearbit(below_pos):
                    if below_pos not in connected_components:
                        connected_components.append(below_pos)
                        list_size_increase = True

                if self.check_gear_or_gearbit(right_pos):
                    if right_pos not in connected_components:
                        connected_components.append(right_pos)
                        list_size_increase = True

                if self.check_gear_or_gearbit(left_pos):
                    if left_pos not in connected_components:
                        connected_components.append(left_pos)
                        list_size_increase = True

        # filter out the gear bits in the list connecting gear bits and gears
        connected_gear_bits: List[tuple] = []
        gear_bits = self.find_gear_bits()
        for comp in connected_components:
            if comp in gear_bits:
                connected_gear_bits.append(comp)

        # return the list of gear_bits whose data flows have to be connected
        return connected_gear_bits

    def synchronize_connected_gear_bits(self):
        """
        Connects the data flows of all gear bits that are connected via gears

        :return:None
        """

        all_gear_bits_until_now = []

        # for each gear bit on the board:
        for gear_bit_pos in self.find_gear_bits():
            # self.write_to_file(f"GearbitPos: {gear_bit_pos}")

            # if the gear bit is not already in the list
            if gear_bit_pos not in all_gear_bits_until_now:
                try:
                    # find all gear bits connected to current gear bit
                    connected_comps = self.connect_gear_bits(gear_bit_pos)
                except Exception as e:
                    self.write_to_file("Bug in connect_gear_bits")
                    self.write_to_file(str(e))
                    raise UserWarning(e)

                # add all identified gear bits connected to current gear bit to the list
                for pos in connected_comps:
                    try:
                        all_gear_bits_until_now.append(pos)
                    except Exception as e:
                        self.write_to_file(str(e))
                try:

                    # obtain the ids of the connected gear bit-bugs
                    ids = [self.bug_matrix[conn_comps] for conn_comps in connected_comps]
                except Exception as e:
                    self.write_to_file("Error in ids = self.bugMatrix(...)")
                    self.write_to_file(str(e))
                    raise UserWarning(e)

                # connect the connected gear bit-bugs
                for id1 in ids:
                    for id2 in ids:
                        self.challenge_implementation.addDataFlow(id1, id2, 0)
                        self.write_to_file(
                            f'T2_Code_Implementation.addDataFlow("{id1}", "{id2}", 0);'
                        )

    def check_gear_or_gearbit(self, pos: tuple) -> bool:
        """
        checks if a position contains a gear or a gear bit

        :param pos: a position on the board
        :return: A Boolean: True if position contains a gear or a gear bit, otherwise False
        """

        # check if the position to check is out of bounds
        if pos[1] < 0 or pos[1] > self._board_shape[1] - 1 or pos[0] < 0 or pos[0] > self._board_shape[0] - 1:
            return False

        # check if the position contains a gear or a gear bit
        elif self.matrix[pos] in [
            self._one_gearbit_rep,
            self._zero_gearbit_rep,
            self._gear_rep,
        ]:
            return True
        else:
            return False

    def find_bits(self) -> List[tuple]:
        """
        Finds the positions of all bits on the board (normal bits AND gear bits).

        :return: a list containing the positions of all bits on the board
        """

        indices = np.where(
            (
                    (self.matrix == self._zero_bit_rep)
                    | (self.matrix == self._one_bit_rep)
                    | (self.matrix == self._one_gearbit_rep)
                    | (self.matrix == self._zero_gearbit_rep)
            )
        )
        ind_list: List[tuple] = []
        for i in range(len(indices[0])):
            ind_list.append((indices[0][i], indices[1][i]))
        return ind_list

    def find_gear_bits(self) -> List[tuple]:
        """
        Finds the positions of all gear bits on the board (ONLY gear bits).

        :return: the positions of all gear bits on the board
        """
        indices = np.where(
            (
                    (self.matrix == self._one_gearbit_rep)
                    | (self.matrix == self._zero_gearbit_rep)
            )
        )
        ind_list: List[tuple] = []
        for i in range(len(indices[0])):
            ind_list.append((indices[0][i], indices[1][i]))
        return ind_list

    def write_to_file(self, text: str):
        """
        Writes a string into a java file that can then be executed later.

        :param text: Java Code as a string
        :return: None
        """

        # read the content of the java file
        with open(self.bugplus_development_path + "Challenge.java", "r") as f:
            contents = f.readlines()

        # add the new text to the lower end of the java file content
        contents[-3] = contents[-3] + "\t\t" + text + "\n"

        # write the modified content back into the java file
        with open(self.bugplus_development_path + "Challenge.java", "w") as f:
            for c in contents:
                f.write(c)

    def addNegBug(self) -> str:
        """
        Adds a negation bug to the program.

        :return: The ID of the newly added bug as a string
        """

        # add a new bug
        self.challenge_implementation.addBug("!", f"!_{self.bug_counter}")
        self.write_to_file(
            f'T2_Code_Implementation.addBug("!", "!_{self.bug_counter}");'
        )

        # connect the data flow of the bug with itself
        self.challenge_implementation.addDataFlow(
            f"!_{self.bug_counter}", f"!_{self.bug_counter}", 0
        )
        self.write_to_file(
            f'T2_Code_Implementation.addDataFlow("!_{self.bug_counter}", "!_{self.bug_counter}", 0);'
        )

        # return the id of the newly added bug
        self.bug_counter += 1
        return f"!_{self.bug_counter - 1}"

    def addDataFlow(
            self,
            id_source_bug: str,
            id_target_bug: str,
            index_data_in: int
    ):
        """
        Adds a data flow from a given source bug to a given target bug

        :param id_source_bug: the id of the source bug
        :param id_target_bug:the id of the target bug
        :param index_data_in: the index of the data in pin that should be used to connect the bugs (0 or 1)
        :return: None
        """
        self.challenge_implementation.addDataFlow(id_source_bug, id_target_bug, index_data_in)

    def connectDataInInterface(
            self,
            id_internal_bug: str,
            index_internal_data_in: int,
            index_external_data_in_interface: int,
    ):
        """
        Connects a data in pin of an internal bug to the data in pin of the external interface

        :param id_internal_bug: the id of the internal bug as it is defined for the Java Bugplus Code (e.g. "!_2")
        :param index_internal_data_in: defines the data in pin of the internal bug that should be connected to the
        DataInInterface. 0 or 1
        :param index_external_data_in_interface: defines the index of the data in pin of the external bug
        (DataInInterface) that should be connected to the internal Bug. 0 or 1
        :return: None
        """
        self.challenge_implementation.connectDataInInterface(
            id_internal_bug, index_internal_data_in, index_external_data_in_interface
        )

    def connectDataOutInterface(self, id_internal_bug: str):
        """
        Connects a data out pin of an internal bug to the data out pin of the external interface

        :param id_internal_bug: id_internal_bug: the id of the internal bug as it is defined for the Java Bugplus Code
        (e.g. "!_2")
        """
        self.challenge_implementation.connectDataOutInterface(id_internal_bug)

    def connectControlInInterface(self, id_internal_bug: str):
        """
        Connects the control flow of the interface with the bit that will be activated first when starting the program.

        :param id_internal_bug: the id of the bug that should be activated first when starting the program.
        :return: None
        """
        self.write_to_file(
            f'T2_Code_Implementation.connectControlInInterface("{id_internal_bug}");'
        )
        self.challenge_implementation.connectControlInInterface(id_internal_bug)

    def addControlFlow(
            self,
            id_source_bug: str,
            index_control_out: int,
            id_target_bug: str
    ):
        """
        Adds a control flow from a given source bug to a given target bug.

        :param id_source_bug: the id of the source bug
        :param index_control_out: the index of the control out pin that should be used to connect the bugs (0 or 1)
        :param id_target_bug: the id of the target bug
        :return:
        """
        self.write_to_file(
            f'T2_Code_Implementation.addControlFlow("{id_source_bug}", 1, "{id_target_bug}");'
        )

        self.challenge_implementation.addControlFlow(
            id_source_bug, index_control_out, id_target_bug
        )
