import numpy as np
from game_data.game.Board import Board


def calculate_risk_areas(board: Board, cluster_tolerance: float = 0):
    risk_evaluation = np.zeros((board.height, board.width))
    existing_cell_occupation = np.array(board.cells)
    risk_evaluation[existing_cell_occupation != 0] = 1

    last_evaluated = {}
    for row in enumerate(risk_evaluation):
        for col in enumerate(row[1]):
            if col[1] == 1:
                last_evaluated[(row[0], col[0])] = 1

    while len(last_evaluated) > 0:
        new_evaluated = {}

        for evaluated_cell in last_evaluated:
            pass
            # TODO:
            #  Evaluate the 8 surrounding cells
            #   -> Note the effect of the different pattern)
            #   -> Note already evaluated cells in risk_evaluation
            #   -> If the cell is already set, manipulate its value
            #  weighting like in player_location_probability
            #  add new to new_evaluated

        # TODO:
        #  Transfer new_evaluated to risk_evaluation
        last_evaluated = new_evaluated

    # TODO:
    #  Cluster the results to 1 * 2, 2 * 2, 2 * 3, ... cells
    #  set as new value the average value of all clustered cells
    #  Note the cluster_tolerance

    return risk_evaluation


if __name__ == "__main__":
    # Test Data
    b = Board(100, 100)
    b[0][0] = 6
    b[2][1] = 2
    b[1][1] = -1
    b[5][6] = 1
    b[15][16] = 1
    print(calculate_risk_areas(b, 0))
