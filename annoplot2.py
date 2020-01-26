import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import datetime


def distance(x1, x2, y1, y2):
    """
    return the Manhattan distance between two points
    """
    return abs(x1 - x2) + abs(y1 - y2)


def annotate(annotations=None, fig=None,
             annmarkerfacecolor: str = 'r', annfacecolor: str = 'w', annedgecolor: str = 'k'):
    # If no figure is specified take the last one. We don't want to use plt.gcf() because if there are no open figures
    # it opens a new empty one
    if fig is None:
        try:
            fig = plt.figure(plt.get_fignums()[-1])
        except IndexError:
            raise (IndexError('There are no open figures'))

    axes = fig.get_axes()
    if type(annotations) is not dict:
        if len(axes) == 1:
            annotations = {axes[0]: annotations}
        else:
            raise (RuntimeError('If the figure has more than 1 axis you need to pass in a dictionary, mapping '
                                'each axis to the corresponding annotations'))
    else:
        if len(annotations) != len(axes):
            raise (RuntimeError('There must be a list of annotations for each axis'))

    antr = Annotator(annotations, fig, annmarkerfacecolor, annfacecolor, annedgecolor)
    fig.canvas.mpl_connect('button_press_event', antr)
    fig.canvas.mpl_connect('key_press_event', antr)


class Annotator:
    def __init__(self, annotations, fig, annmarkerfacecolor: str, annfacecolor: str, annedgecolor: str):
        self.annotations = annotations
        self.fig = fig
        self.annmarkerfacecolor = annmarkerfacecolor
        self.annfacecolor = annfacecolor
        self.annedgecolor = annedgecolor

        self.drawn_annotation = {}
        self.shown = {}
        for ax in fig.get_axes():
            self.shown[ax] = None
            self.drawn_annotation[ax] = None

    def __call__(self, event):
        ax = event.inaxes
        if ax is None:
            ax = plt.gca()

        click_x = event.xdata
        click_y = event.ydata

        if event.name == 'button_press_event' and (click_x is None or click_y is None):
            return

        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]

        arguments = [ax, click_x, click_y, x_range, y_range]

        if len(ax.lines) > 0 and len(ax.images) == 0:
            self._manage_plot(event, arguments)
        elif len(ax.lines) == 0 and len(ax.images) > 0:
            pass
        else:
            raise (RuntimeError('Annotations can only be added to an Axis that either contains Lines or Images'))

    def _manage_plot(self, event, arguments):

        ax, click_x, click_y, x_range, y_range = arguments

        axis_annotations = self.annotations[ax]

        if event.name == 'button_press_event':
            min_idx = None
            min_dist = np.inf

            annotation = None
            lines = ax.lines
            for i, l in enumerate(lines):
                xdata = l.get_xdata()
                ydata = l.get_ydata()
                for j in range(len(xdata)):
                    x = xdata[j]
                    y = ydata[j]
                    if isinstance(x, datetime.datetime):
                        x = mdates.date2num(x)
                    if isinstance(y, datetime.datetime):
                        y = mdates.date2num(y)

                    dist = distance(x / x_range, click_x / x_range, y / y_range, click_y / y_range)
                    if dist < min_dist:
                        try:
                            annotation = [x, y, axis_annotations[i][j]]
                        except IndexError:
                            annotation = [x, y, None]
                        min_dist = dist
                        min_idx = (i, j)

            x, y, a = annotation
            self._draw_annotation(ax, x, y, a)
            self.shown[ax] = min_idx

        elif event.name == 'key_press_event':
            bkup_shown = self.shown[ax]
            if self.shown[ax] is None:
                return

            i, j = self.shown[ax]
            line = ax.lines[i]

            delta = 0
            if event.key == 'left':
                if j == 0:
                    return
                delta = -1
            elif event.key == 'right':
                if j == line.get_xdata().size - 1:
                    return
                delta = 1
            elif event.key == 'escape' or event.key == 'delete':
                self._clear_annotation(ax)
                return

            x = line.get_xdata()[j + delta]
            y = line.get_ydata()[j + delta]
            try:
                a = axis_annotations[i][j + delta]
            except IndexError:
                a = None

            self._draw_annotation(ax, x, y, a)
            self.shown[ax] = (bkup_shown[0], bkup_shown[1] + delta)

    def _draw_annotation(self, ax, x, y, annotation):
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        deltax = (xlim[1] - xlim[0]) / 50
        deltay = (ylim[1] - ylim[0]) / 50

        self._clear_annotation(ax)

        if annotation is not None:
            text = '{:.4f}, {:.4f}\n{}'.format(x, y, annotation)
        else:
            text = '{:.4f}, {:.4f}'.format(x, y)

        t = ax.text(x + deltax, y + deltay, text, bbox={'facecolor': self.annfacecolor, 'edgecolor': self.annedgecolor})

        m = ax.scatter([x], [y], marker='s', c=self.annmarkerfacecolor, zorder=100)
        self.drawn_annotation[ax] = (t, m)

        ax.figure.canvas.draw_idle()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

    def _clear_annotation(self, ax):
        if self.drawn_annotation[ax] is not None:
            self.drawn_annotation[ax][0].remove()
            self.drawn_annotation[ax][1].remove()
            self.shown[ax] = None
            self.drawn_annotation[ax] = None

        self.fig.canvas.draw_idle()
