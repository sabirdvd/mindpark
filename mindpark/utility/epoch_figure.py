import numpy as np
from matplotlib.ticker import FuncFormatter, MaxNLocator
from mindpark.utility.deviation_figure import DeviationFigure


class EpochFigure(DeviationFigure):

    """
    A deviation figure where time axes are grouped based on an epoch size and
    duration information for the lines.
    """

    def __init__(self, charts, title, epochs, resolution=1):
        super().__init__(charts, title)
        self._epochs = epochs
        self._resolution = resolution
        self._bins = (1 + epochs) * resolution

    def add(self, title, xlabel, ylabel, lines):
        """
        Add a chart to the figure. Lines is a dictionary mapping from names to
        nested lists over repeats, epochs, and episodes.
        """
        lines = {k: self._pad(self._average(v)) for k, v in lines.items()}
        last_tick = (self._epochs + 1) - 1 / self._resolution
        domain = np.linspace(0, last_tick, self._bins)
        ax = super().add(title, xlabel, ylabel, domain, lines)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: str(int(x))))
        self._align_markers_at_ticks(ax)

    def _average(self, line):
        """
        Average over the episodes of each epoch, converting the line from
        dimensions (repeats, epochs, episodes) to (repeats, bins).
        """
        repeats = []
        for repeat in line:
            repeats.append([])
            for epoch in repeat:
                bins = self._chunk(epoch, self._resolution)
                bins = [np.mean(x) if len(x) else np.nan for x in bins]
                repeats[-1] += bins
        return repeats

    def _pad(self, line):
        """
        Convert the line from a list of dimensions (repeats, epochs) to a nan
        padded Numpy array of dimensions (epochs, repeats).
        """
        padded = np.empty((len(line), self._bins))
        padded[:] = np.nan
        for repeat, values in enumerate(line):
            padded[repeat, :len(values)] = values
        return padded.T

    def _align_markers_at_ticks(self, ax):
        ticks = ax.xaxis.get_major_locator()()
        ticks = [int(x) * self._resolution for x in ticks if x <= self._epochs]
        ax.lines[0].set_markevery(ticks)

    @staticmethod
    def _chunk(collection, bins):
        splitted = [[] for _ in range(bins)]
        for index, value in enumerate(collection):
            chunk = index * bins / len(collection)
            splitted[int(chunk)].append(value)
        return splitted