"""
Translator (T1) from CF matrix to graphical TT board
with help of functions defined in aux_partial_orderer.py
and aux_matrix_to_image.py
"""

# standard library imports
from typing import Optional, Tuple

# 3rd party imports
from igraph import *

# local imports (i.e. our own code)
from aux_partial_orderer import PartialOrderer
from aux_matrix_to_image import *


# noinspection PyShadowingNames
class RankBasedTranslator:
    num_bits = None
    rows = None
    columns = None
    matrix = None
    g = None
    colors = None

    def __init__(
            self,
            rows: Optional[int] = 20,
            columns: Optional[int] = 20
    ):
        """
        Builds empty TT board (of dimension rows x columns) as graph.
        Graph is diamond grid-shaped: each node is only connected to its direct diagonal neighbours.

        :param rows: number of rows in the TT grid
        :param columns: number of columns in the TT grid
        """
        self.rows = rows
        self.columns = columns
        self.matrix = np.zeros(shape=(rows, columns), dtype=np.int64)

        coordinates = []
        self.edges = []
        count = 0
        for i in range(self.rows):
            for j in range(self.columns):
                coordinates.append((i, j))
                if i % 2 != j % 2:
                    if i < self.rows - 1:

                        if j != 0:
                            self.edges.append((count, count + self.columns - 1))
                        if j != self.columns - 1:
                            self.edges.append((count, count + self.columns + 1))

                        if j != 0 and j != self.columns - 1:
                            pass
                        else:
                            pass
                    else:
                        self.edges.append((count, self.rows * self.columns))

                count += 1
        coordinates.append((self.rows, self.columns))

        self.g = Graph(directed=True)

        self.g.add_vertices(self.rows * self.columns + 1, attributes={"coordinates": coordinates})
        self.g.vs["name"] = coordinates
        self.g.vs["label"] = self.g.vs["name"]
        self.colors = ["lightgrey"] * (self.rows * self.columns + 1)

        # print(f"Edges: {edges}")
        self.g.add_edges(self.edges)

    def place_bits(self, rankings: list) -> List[Tuple]:
        """
        Generates coordinates to place pieces on from page ranks.

        :param rankings: list of page ranks
        :return: coordinates: list of position of TT bits on board.
        """
        coordinates = []
        print(f"Ranks: {rankings}")
        levels = len(rankings)
        # we have to leave the last rows open to possibly add intercept tokens
        placing_rows = np.ceil(np.linspace(start=0, stop=self.rows - 3, num=levels))
        print(placing_rows)
        for i in range(levels):
            length = 1
            try:
                length = len(rankings[i])
            except:
                length = 1
            if length != 1:
                print(f"Linspace {(np.linspace(0, self.columns, num=length))}")
                columns = np.ceil(np.linspace(0, self.columns, num=length + 2))[1:-1]
            else:
                columns = [np.ceil(np.linspace(0, self.columns, num=length + 2))[1]]
                print(f"f Columns: {columns}")
            for j in range(length):
                if placing_rows[i] % 2 == columns[j] % 2:
                    columns[j] -= 1
                coordinates.append((placing_rows[i], columns[j]))

            # place Bits in Matrix
            for (x, y) in coordinates:
                self.matrix[int(x)][int(y)] = parts["BlueLeft"]
        return coordinates

    def find_shortest_paths(
            self,
            bit_coordinates: List[Tuple],
            matrix: np.ndarray
    ) -> List[List]:
        """
        Identifies placement of connecting pieces between bits.

        :param bit_coordinates: placement of bits on TT board.
        :param matrix: adjacency matrix of graph acting as empty TT board.
        :return: shortest_paths: IDs of nodes traversed on shortest paths between bits.
        """
        bit_ids = []
        for (i, j) in bit_coordinates:
            bit_ids.append(i * self.columns + j)
        print(f"Bit IDS: {bit_ids}")

        for bid in bit_ids:
            self.colors[int(bid)] = "blue"
        self.g.vs["color"] = self.colors

        print(f"Bit Coordinates {bit_coordinates}")
        children = PartialOrderer.order(matrix)

        for i in range(len(bit_ids)):
            for j in children[i]:
                shortest_paths = []
                all_ids_without_ij = []
                for b in bit_ids:
                    if b != bit_ids[i] and b != bit_ids[j]:
                        all_ids_without_ij.append(int(b))

                delete_edges = []
                for edge in self.edges:
                    for id in all_ids_without_ij:
                        if edge[0] == id or edge[1] == id:
                            delete_edges.append(edge)

                self.g.delete_edges(delete_edges)

                j = int(j)
                i = int(i)
                print(f"I {i}, {j}")
                left_child_id = int(bit_ids[i] + self.columns - 1)
                right_child_id = int(bit_ids[i] + self.columns + 1)
                left_child_coord = self.get_coordinate(left_child_id)
                right_child_coord = self.get_coordinate(right_child_id)
                print(f"COORDS: {left_child_coord}")
                if j == 0:
                    print("Link to Sink Node")
                    print(f"Path from {i}({bit_ids[i]}) to Sink Node)")

                    if self.matrix[left_child_coord[0]][left_child_coord[1]] == 0:
                        shortest_paths.append(self.g.get_shortest_paths(left_child_id, self.rows * self.columns)[0])
                        self.create_board(shortest_paths)
                    else:
                        shortest_paths.append(self.g.get_shortest_paths(right_child_id, self.rows * self.columns)[0])
                        self.create_board(shortest_paths)
                    self.g.add_edges(delete_edges)
                    continue
                print(f"f Path from {i}({bit_ids[i]}) to {j}({bit_ids[j]})")
                if self.matrix[left_child_coord[0]][left_child_coord[1]] == 0:
                    shortest_paths.append(self.g.get_shortest_paths(left_child_id, int(bit_ids[j]))[0])

                else:
                    shortest_paths.append(self.g.get_shortest_paths(right_child_id, int(bit_ids[j]))[0])

                self.create_board(shortest_paths)
                self.g.add_edges(delete_edges)
        return shortest_paths

    def create_board(self, shortest_paths: List[List]):
        """
        Auxiliary function to generate auxiliary matrix for Jesse Crossen simulator

        :param shortest_paths: nodes on shortest paths between bits on TT board graph.
        """
        print(f"SHORTEST PATHS: {shortest_paths}")
        for path in shortest_paths:
            coordinates = [(int(i / self.columns), i % self.columns) for i in path]
            print(coordinates)
            for i in range(0, len(coordinates) - 1):
                print(f"1. {coordinates[i]} , 2. {coordinates[i + 1]}")
                if coordinates[i][1] > coordinates[i + 1][1]:
                    if self.matrix[coordinates[i]] == parts["BlueLeft"]:  # there are only zeros
                        continue
                    if self.matrix[coordinates[i]] == parts["GreenRight"]:
                        self.matrix[coordinates[i]] = parts["Orange"]
                        self.colors[self.get_id(coordinates[i])] = "orange"

                    else:
                        self.matrix[coordinates[i]] = parts["GreenLeft"]
                        self.colors[self.get_id(coordinates[i])] = "darkgreen"
                    self.g.vs["color"] = self.colors
                else:
                    if self.matrix[coordinates[i]] == parts["BlueLeft"]:
                        continue

                    if self.matrix[coordinates[i]] == parts["GreenLeft"]:
                        self.matrix[coordinates[i]] = parts["Orange"]
                        self.colors[self.get_id(coordinates[i])] = "orange"

                    else:
                        self.matrix[coordinates[i]] = parts["GreenRight"]
                        self.colors[self.get_id(coordinates[i])] = "lightgreen"
                    self.g.vs["color"] = self.colors

        print(self.matrix)

    def set_intercepts(
            self,
            matrix: np.ndarray,
            bit_coordinates: List[Tuple]
    ) -> List[Tuple]:
        """
        Add intercepting pieces on board below bits that connect to none.

        :param matrix: unfinished auxiliary matrix for Jesse Crossen simulator
        :param bit_coordinates: position of bits on TT board.
        :return: intercept_coords: position of intercepting pieces on TT board.
        """
        count = 0
        intercept_coords = []
        for col in range(len(matrix[0])):
            only_zeros = True
            for row in range(len(matrix)):
                if matrix[row][col] != 0:
                    only_zeros = False
                    break
            if only_zeros:
                if col % 2 == 0:
                    index = int(col / 2)
                    coord = (bit_coordinates[index][0] + 1, bit_coordinates[index][1] - 1)
                    intercept_coords.append(coord)
                else:
                    # print(bit_coordinates)
                    index = int(col / 2)
                    coord = (bit_coordinates[index][0] + 1, bit_coordinates[index][1] + 1)
                    intercept_coords.append(coord)

        # print(interceptCoords)
        for ic in intercept_coords:
            self.matrix[int(ic[0])][int(ic[1])] = parts["Black"]
            self.colors[self.get_id(ic)] = "Black"
            self.g.vs["color"] = self.colors
        return intercept_coords

    def get_coordinate(self, identifier: int) -> Tuple[int, int]:
        """
        Auxiliary function to transform node ID in aux. graph into coordinates in aux. matrix

        :param identifier: node ID in graph
        :return: tuple of row and column number in aux. matrix
        """
        return int(identifier / self.columns), int(identifier % self.columns)

    def get_id(self, coordinate: Tuple[int, int]) -> int:
        """
        Auxiliary function to transform coordinate in aux. TT matrix into ID in aux. graph

        :param coordinate: tuple of row and column number in aux. matrix
        :return: node ID in graph
        """
        return int(coordinate[0]) * self.columns + int(coordinate[1])


def cf_matrix_to_board(mat):
    ranking = PartialOrderer.calc_rank(PartialOrderer.order(mat))
    translator = RankBasedTranslator(27, 15)

    bit_coordinates = translator.place_bits(ranking)
    translator.set_intercepts(mat, bit_coordinates)

    shortest_paths = translator.find_shortest_paths(bit_coordinates, mat)
    translator.create_board(shortest_paths)

    print("MAT:")
    print(translator.matrix)

    layout = translator.g.layout_grid(width=translator.columns)
    plot(translator.g, layout=layout)
    print("NEW BOARD")
    open_new_board(translator.matrix)


if __name__ == "__main__":
    matrix = [[0, 1, 0, 0, 0, 1],
              [1, 0, 0, 0, 0, 0],
              [0, 0, 1, 1, 0, 0]]

    matrix_2 = [[0, 0, 0, 0, 0, 1],
                [0, 1, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0]]

    matrix_3 = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0]
    ]

    cf_matrix_to_board(matrix_3)
