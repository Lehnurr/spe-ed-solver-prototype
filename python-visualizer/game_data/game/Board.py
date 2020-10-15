from copy import deepcopy


class Board:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cell_count = self.width * self.height
        self.cells = [[0 for x in range(width)] for y in range(height)]

    def __getitem__(self, row_index):
        return self.cells[row_index]

    def set_cell(self, x: int, y: int, value: int):
        if not self.point_is_on_board(x, y):
            return
        if self.cells[y][x] == 0:
            self.cells[y][x] = value
        else:
            self.cells[y][x] = -1

    def point_is_on_board(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def point_is_available(self, x: int, y: int) -> bool:
        return self.point_is_on_board(x, y) and self.cells[y][x] == 0

    def get_neighbors(self, x, y):
        x1 = x - 1 if x > 0 else x
        y1 = y - 1 if y > 0 else y
        x2 = x + 1 if x + 1 < self.width else x
        y2 = y + 1 if y + 1 < self.height else y
        # get all neighbors the center cell
        neighbors_and_i = list(self.get_points_in_rectangle(x1, y1, x2, y2))
        # remove the center-cell
        neighbors_and_i.remove((x, y))
        return neighbors_and_i

    def copy(self):
        copy = Board(self.width, self.height)
        copy.cells = deepcopy(self.cells)
        return copy

    @staticmethod
    def get_points_in_rectangle(x1, y1, x2, y2):
        x_from = min(x1, x2)
        x_to = max(x1, x2) + 1
        y_from = min(y1, y2)
        y_to = max(y1, y2) + 1

        for x in range(x_from, x_to):
            for y in range(y_from, y_to):
                yield x, y
