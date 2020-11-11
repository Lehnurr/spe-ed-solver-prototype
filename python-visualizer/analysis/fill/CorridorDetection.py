import numpy as np
from analysis.area_detection import safe_area_detection


class CorridorDetection:

    def __init__(self):
        self.corridor_lut = [CorridorDetection.__generate_lut_element(key) for key in range(512)]
        print(self.corridor_lut)

    @staticmethod
    def __generate_lut_element(key: int) -> bool:
        flat_working_array = np.zeros(9)
        pos = 0
        while key > 0:
            if key & 1:
                flat_working_array[pos] = 1.
            key >>= 1
            pos += 1
        working_array = flat_working_array.reshape((3, 3))
        original_area_count = safe_area_detection.count_safe_areas(working_array)
        working_array[1, 1] = 1.
        changed_area_count = safe_area_detection.count_safe_areas(working_array)
        return original_area_count != changed_area_count


if __name__ == "__main__":
    cd = CorridorDetection()
