"""
Generate page rank scores and a list of connected bits from CF matrix.
"""
# standard library imports
from typing import List

# 3rd party imports
import numpy as np
from igraph import *


class PartialOrderer:
    @classmethod
    def order(cls, cf_matrix: np.ndarray) -> List[List]:
        """
        For n (bug)bits in the CF matrix, return IDs of node connected to control-out pins.

        :param cf_matrix: a matrix of dimensions n x 2n
        :return: fathers: a list of n sub-lists.
        """
        num_bugs = len(cf_matrix)
        fathers = []
        for column in range(num_bugs):
            following_nodes = []
            for row in range(num_bugs):
                if cf_matrix[row][2 * column] == 1:
                    following_nodes.append(row)
            for row in range(num_bugs):
                if cf_matrix[row][2 * column + 1] == 1:
                    following_nodes.append(row)
            fathers.append(following_nodes)

        return fathers

    @classmethod
    def calc_rank(cls, fathers: list) -> List:
        """
        Calculate the page rank of each bit

        :param fathers: List of n sub-lists
        :return: ranking: List of page ranks of length n
        """
        print(f"Children: {fathers}")
        all_nodes = [i for i in range(len(fathers))]
        ranking = []

        # create Graph
        g = Graph(directed=True)
        g.add_vertices(len(all_nodes), attributes={"label": range(len(all_nodes))})
        for parent in range(len(fathers)):
            for child in fathers[parent]:
                if child == 0:
                    continue
                g.add_edges([(parent, child)])
        plot(g)

        ranks = g.pagerank(directed=True)

        added_to_rank_count = 0
        while added_to_rank_count != len(all_nodes):
            max_rank = min(ranks)
            current_rank_bits = []
            for i in range(len(ranks)):
                if ranks[i] == max_rank:
                    current_rank_bits.append(i)
                    added_to_rank_count += 1
                    ranks[i] = np.inf
            # ranks.remove(maxrank)
            ranking.append(current_rank_bits)

        print(ranking)
        return ranking
