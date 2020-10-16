from enum import Enum
from typing import Tuple, List, Dict

import numpy as np
from game_data.game.Board import Board


def calculate_risk_areas(board: Board, cluster_tolerance: float = 0):
    risk_evaluation = np.zeros((board.height, board.width))
    existing_cell_occupation = np.array(board.cells)
    risk_evaluation[existing_cell_occupation != 0] = 1

    rows, cols = np.where(risk_evaluation == 1)
    rows = list(rows)
    cols = list(cols)

    # Add the top board border
    rows += [-1] * board.width
    cols += range(0, board.width)

    # Add the bottom board border
    rows += [board.height] * board.width
    cols += range(0, board.width)

    # Add the left board border
    cols += [-1] * board.height
    rows += range(0, board.height)

    # Add the right board border
    cols += [board.width] * board.height
    rows += range(0, board.height)

    last_evaluated = {(cols[index], rows[index]): 1 for index in range(0, len(rows))}

    while len(last_evaluated) > 0:
        print(np.count_nonzero(risk_evaluation))

        # Get neighbors of last evaluated
        to_be_evaluated: Dict[Tuple[int, int], RiskClass] = {}
        for last in last_evaluated.keys():
            for neighbor in board.get_neighbors(last[0], last[1]):
                if not neighbor or risk_evaluation[neighbor[1]][neighbor[0]] > 0 or neighbor in to_be_evaluated:
                    continue
                neighbors_risk_clockwise = [(1 if i is None else risk_evaluation[neighbor[1], neighbor[0]]) for i in
                                            board.get_neighbors(neighbor[0], neighbor[1])]
                to_be_evaluated[neighbor] = RiskClass(0, neighbors_risk_clockwise)

        last_evaluated.clear()

        # Sort neighbors by pattern weight
        to_be_evaluated = {k: v for k, v in sorted(to_be_evaluated.items(), key=lambda item: item[1].pattern.value[2])}

        for n in to_be_evaluated.items():
            position = n[0]
            neighbors_risk_clockwise = [(1 if i is None else risk_evaluation[position[1], position[0]]) for i in
                                        board.get_neighbors(position[0], position[1])]

            # Set neighbors neighbors new & calculate risk
            n[1].set_neighbors(neighbors_risk_clockwise)
            # Add the neighbor to last evaluated
            last_evaluated[position] = n[1]
            # Add the neighbor to risk evaluation
            risk_evaluation[position[1]][position[0]] = n[1].get_risk()

    # TODO:
    #  Cluster the results to 1 * 2, 2 * 2, 2 * 3, ... cells
    #  set as new value the average value of all clustered cells
    #  Note the cluster_tolerance
    #  Cluster also cells with value 1!!!!

    if cluster_tolerance > 0:
        raise Exception("Clustering is not implemented")

    return risk_evaluation


class RiskClass:
    def __init__(self, center_risk, neighbors_risk_clockwise: List[float]):
        self.__risk = None
        self.__center_risk = center_risk
        self.__neighbors_risk_clockwise = None
        self.pattern = None
        self.set_neighbors(neighbors_risk_clockwise)

    def get_risk(self):
        if self.__center_risk:
            return self.__center_risk
        elif self.__risk:
            return self.__risk
        elif self.__neighbors_risk_clockwise and self.pattern:
            neighbors_sorted = self.__neighbors_risk_clockwise.copy()
            neighbors_sorted.sort()
            weighted_sum = 0.
            quantity = 0.
            for neighbor in enumerate(neighbors_sorted):
                if neighbor[1] == 0:
                    # weight unweighted with 0.25
                    quantity += 0.25
                elif neighbor[0] < self.pattern.value[1]:
                    # weight low neighbors with 0.65
                    weighted_sum = neighbor[1] * 0.65
                    quantity += 0.5
                else:
                    # weight high neighbors individual
                    weighted_sum += neighbor[1] * self.pattern.value[2]
                    quantity += self.pattern.value[2]

            self.__risk = weighted_sum / quantity
            return self.__risk
        else:
            return self.__center_risk

    def set_neighbors(self, neighbors_risk_clockwise: List[float]):
        self.__neighbors_risk_clockwise = neighbors_risk_clockwise
        self.__risk = None
        self.pattern = RiskPattern.get_risk_pattern(neighbors_risk_clockwise)


class RiskPattern(Enum):
    # (Pattern, number_of_low_neighbors, weighting of the high values)
    Surrounded = ("HHHH", 0, 1)
    DeadEnd = ("HHHL", 1, 2)
    Corner = ("HHLL", 2, 1.5)
    Lane = ("HLHL", 2, 1)
    Obstacle = ("HLLL", 3, 0.75)
    Empty = ("LLLL", 4, 0)

    @staticmethod
    def get_risk_pattern(neighbors_risk_clockwise: List[float]):
        neighbors_sorted = neighbors_risk_clockwise.copy()
        neighbors_sorted.sort()

        neighbor_differences = [
            (neighbors_sorted[i], neighbors_sorted[i + 1] - neighbors_sorted[i])
            for i in range(0, len(neighbors_sorted) - 1)
        ]

        low_limit = max(neighbor_differences, key=lambda difference_tuple: difference_tuple[1])

        actual_pattern = ''.join(['H' if neighbor > low_limit[0] else 'L' for neighbor in neighbors_risk_clockwise])
        for pattern in RiskPattern:
            if actual_pattern in pattern.value[0] * 2:
                return pattern

        return RiskPattern.Surrounded


if __name__ == "__main__":
    # Test Data
    b = Board(10, 11)
    b[0][0] = 6
    b[2][1] = 2
    b[1][1] = -1
    b[5][6] = 1
    print(calculate_risk_areas(b))
