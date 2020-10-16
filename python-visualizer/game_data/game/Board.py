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

    # returns the direct neighbors clockwise, starts with the left neighbor
    def get_neighbors(self, x, y):
        return [
            (x - 1, y) if self.point_is_on_board(x - 1, y) else None,
            (x, y - 1) if self.point_is_on_board(x, y - 1) else None,
            (x + 1, y) if self.point_is_on_board(x + 1, y) else None,
            (x, y + 1) if self.point_is_on_board(x, y + 1) else None
        ]

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
