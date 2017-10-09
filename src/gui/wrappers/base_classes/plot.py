import numpy as np
from PyQt5.QtWidgets import QSizePolicy
from matplotlib.axes import Axes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse


class Plot(FigureCanvas):
    def __init__(self, parent=None, dpi=100):
        super(Plot, self).__init__(figure=Figure(dpi=dpi))
        self.setParent(parent)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.updateGeometry()
        self.figure.set_facecolor((1, 1, 1, 0))
        self._add_sub_plot()

        self.plot()

    def _add_sub_plot(self):
        self.ax = self.figure.add_subplot(111, aspect='auto', frameon=False)  # type: Axes
        self.ax.axes.get_xaxis().set_visible(False)
        self.ax.axes.get_yaxis().set_visible(False)
        self.ax.margins(tight=True)
        self.figure.tight_layout(pad=0)

    def plot(self):
        NUM = 250

        ells = [
            Ellipse(
                xy=np.random.rand(2) * 10,
                width=np.random.rand(),
                height=np.random.rand(),
                angle=np.random.rand() * 360
            ) for _ in range(NUM)
        ]

        for e in ells:
            self.ax.add_artist(e)
            e.set_clip_box(self.ax.bbox)
            e.set_alpha(np.random.rand())
            e.set_facecolor(np.random.rand(3))
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.draw()
