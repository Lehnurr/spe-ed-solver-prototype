import numpy as np
from typing import List
from typing import Tuple
from skimage import measure


class SafeArea:

    def __init__(self):
        self.points = []

    def join(self, other):
        self.points += other.points


# returns tuple of list of found areas and image of input size with ids of corresponding idx in list
def detect_safe_areas(input_array: np.ndarray) -> Tuple[List[SafeArea], np.ndarray]:
    working_array = np.ones(input_array.shape)
    working_array[input_array != 0] = 0
    labels = measure.label(working_array, background=0, connectivity=1)

    detected_area_count = np.max(labels)

    result_area_list = [SafeArea() for i in range(detected_area_count)]
    indexes = np.int_(np.ones(working_array.shape) * -1)

    for y in range(working_array.shape[0]):
        for x in range(working_array.shape[1]):
            idx = labels[y, x] - 1
            indexes[y, x] = idx
            if idx >= 0:
                result_area_list[idx].points.append((x, y))

    return result_area_list, indexes
