from visualisation import SliceViewer
import numpy as np


WIDTH = 64
HEIGHT = 32

DEMO_SLICES = 50

sliceViewer = SliceViewer.SliceViewer(WIDTH, HEIGHT, ["a", "b", "c"])

for sliceIdx in range(DEMO_SLICES):
    sliceViewer.add_data("a", np.ones((HEIGHT, WIDTH)) * sliceIdx)
    sliceViewer.add_data("b", np.random.randint(-100, 200, (HEIGHT, WIDTH)))
    sliceViewer.add_data("c", np.ones((HEIGHT, WIDTH)) * 30)
    sliceViewer.next_step()

sliceViewer.show_slices()


