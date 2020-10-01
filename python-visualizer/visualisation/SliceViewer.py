import numpy as np
import matplotlib.pyplot as plt


# based on https://matplotlib.org/3.2.1/gallery/event_handling/image_slices_viewer.html
class SliceViewer:
    def __init__(self, ax, data):
        self.ax = ax
        ax.set_title('use scroll wheel to navigate images')

        self.data = data
        self.slices, rows, cols, colDims = data.shape
        self.ind = 0

        self.im = ax.imshow(self.data[self.ind, :, :, :])
        self.update()

    def on_scroll(self, event):
        if event.button == 'up':
            self.ind = (self.ind + 1) % self.slices
        elif event.button == 'down':
            self.ind = (self.ind - 1) % self.slices
        self.update()

    def update(self):
        self.im.set_data(self.data[self.ind, :, :, :])
        self.ax.set_ylabel('slice %s' % self.ind)
        self.im.axes.figure.canvas.draw()


def show_numpy_slice_viewer(numpy_slices):
    fig, ax = plt.subplots(1, 1)
    tracker = SliceViewer(ax, numpy_slices)
    fig.canvas.mpl_connect('scroll_event', tracker.on_scroll)
    plt.show()
