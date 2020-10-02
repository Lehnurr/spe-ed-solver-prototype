import numpy as np
import matplotlib.pyplot as plt
import math


COLOR_MAP_NAME = "inferno"


class SliceViewer:

    def __init__(self, plot_width, plot_height, attribute_names_list):

        self.showIdx = 0

        assert(plot_width > 0)
        self.plot_width = plot_width

        assert(plot_height > 0)
        self.plot_height = plot_height

        self.attributeNamesList = list(attribute_names_list)

        self.currentDataMapping = {}
        self.dataMappings = []

        self.axMapping = {}
        self.plotMapping = {}

        plot_count = len(attribute_names_list)
        plots_horizontal_count = int(math.ceil(math.sqrt(plot_count)))
        plots_vertical_count = int(math.ceil(plot_count / plots_horizontal_count))

        self.fig = plt.figure()
        sync_axis = None

        initialisation_array = np.zeros((plot_height, plot_width))
        initialisation_array[0, 0] = 1

        for attribute_idx, attribute_name in enumerate(attribute_names_list):
            if not sync_axis:
                ax = plt.subplot(plots_vertical_count, plots_horizontal_count, attribute_idx + 1)
                sync_axis = ax
            else:
                ax = plt.subplot(plots_vertical_count, plots_horizontal_count, attribute_idx + 1,
                                 sharex=sync_axis, sharey=sync_axis)
            ax.set_title(attribute_name)
            ax.xaxis.tick_top()
            self.axMapping[attribute_name] = ax
            self.plotMapping[attribute_name] = ax.imshow(initialisation_array, cmap=plt.get_cmap(COLOR_MAP_NAME))

    def on_scroll(self, event):
        if event.button == 'up':
            self.showIdx = (self.showIdx + 1) % len(self.dataMappings)
        elif event.button == 'down':
            self.showIdx = (self.showIdx - 1) % len(self.dataMappings)
        self.update()

    def update(self):
        for attribute_name, attribute_data in self.dataMappings[self.showIdx].items():
            assert (attribute_data is not None)
            im = self.plotMapping[attribute_name]
            im.set_data(attribute_data)
            self.axMapping[attribute_name].relim()
            self.axMapping[attribute_name].autoscale_view()
        self.fig.suptitle(f"Slice ({self.showIdx})")
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def add_data(self, attribute_name: str, data: np.array):
        assert(attribute_name in self.attributeNamesList)
        max_value = np.max(data)
        min_value = np.min(data)
        difference = max_value - min_value
        if difference != 0:
            self.currentDataMapping[attribute_name] = (data + math.fabs(min_value)) / math.fabs(difference)
        else:
            self.currentDataMapping[attribute_name] = np.ones((self.plot_height, self.plot_width))

    def next_step(self):
        self.dataMappings.append(self.currentDataMapping)
        self.currentDataMapping = {}

    def show_slices(self):
        assert(len(self.dataMappings) > 0)
        self.update()
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        plt.show()
