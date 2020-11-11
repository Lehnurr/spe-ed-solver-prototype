import numpy as np
from analysis.area_detection import safe_area_detection
import matplotlib.pyplot as plt
from itertools import product
import time


class CorridorDetection:

    def __init__(self):
        self.corridor_lut = [CorridorDetection.__generate_lut_element(key) for key in range(512)]

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

    @staticmethod
    def __generate_key(input_array: np.ndarray) -> int:
        input_binary = np.zeros(input_array.shape, dtype=bool)
        input_binary[input_array != 0] = True
        key_bytes = np.packbits(input_binary.flatten())
        key = (key_bytes[0] << 1) + (key_bytes[1] >> 7)
        return key

    def get_corridor_map(self, input_array: np.ndarray) -> np.ndarray:
        height, width = input_array.shape
        padded_array = np.pad(input_array, 1, mode="constant", constant_values=1)
        output_array = np.zeros(input_array.shape)
        for y, x in product(range(height), range(width)):
            cut_out_area = padded_array[y:y+3, x:x+3]
            key = CorridorDetection.__generate_key(cut_out_area)
            output_array[y, x] = self.corridor_lut[key]
        return output_array


if __name__ == "__main__":
    cd = CorridorDetection()
    test_array = np.random.randint(2, size=(200, 200))
    start_time = time.time()
    test_result = cd.get_corridor_map(test_array)
    print(time.time() - start_time)

    fig = plt.figure()
    ax1 = plt.subplot(211)
    plt.imshow(test_array)
    ax2 = plt.subplot(212, sharex=ax1, sharey=ax1)
    plt.imshow(test_result)
    plt.show()

