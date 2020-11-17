class DrawingPatternPoint:
    def __init__(self, x_change: int, y_change: int, is_obligatory: bool = True):
        self.x_change = x_change
        self.y_change = y_change
        self.is_obligatory = is_obligatory

    def copy(self):
        return DrawingPatternPoint(self.x_change, self.y_change, self.is_obligatory)

    def copy_invert(self):
        return DrawingPatternPoint(-self.x_change, -self.y_change, self.is_obligatory)
