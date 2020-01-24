from abc import ABC, abstractmethod

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import datetime


def _manage_kwargs(kwargs):
    extra_args = {}
    available_args = ['annmarkerfacecolor', 'annfacecolor', 'annedgecolor']
    for arg in available_args:
        if arg in kwargs:
            extra_args[arg] = kwargs[arg]
            del kwargs[arg]

    return extra_args


def distance(x1, x2, y1, y2):
    """
    return the Manhattan distance between two points
    """
    return abs(x1 - x2) + abs(y1 - y2)


def annotate(annotations=None, fig=None, **kwargs):
    # If no figure is specified take the last one
    if fig is None:
        try:
            fig = plt.figure(plt.get_fignums()[-1])
        except IndexError:
            raise(IndexError('There are no open figures'))

    extra_args = _manage_kwargs(kwargs)

    axes = fig.get_axes()
    if type(annotations) is not dict:
        if len(axes) == 1:
            annotations = {axes[0]: annotations}
        else:
            raise(RuntimeError('If the figure has more than 1 axis you need to pass in a dictionary, mapping'
                               'each axis to the corresponding annotations'))
    else:
        if len(annotations) != len(axes):
            raise (RuntimeError('There must be a list of annotations for each axis'))

    antr = PlotAnnotator(annotations, fig, **extra_args)
    fig.canvas.mpl_connect('button_press_event', antr)
    fig.canvas.mpl_connect('key_press_event', antr)


class Annotator(ABC):
    def __init__(self, annotations, fig, annmarkerfacecolor: str, annfacecolor: str, annedgecolor: str):
        self.annotations = annotations
        self.fig = fig
        self.annmarkerfacecolor = annmarkerfacecolor
        self.annfacecolor = annfacecolor
        self.annedgecolor = annedgecolor

        self.drawn_annotation = None
        self.shown = None

    def clear_shown_element(self):
        self.shown = None

    def clear_annotation(self):
        if self.drawn_annotation is not None:
            self.drawn_annotation[0].remove()
            self.drawn_annotation[1].remove()
            self.clear_shown_element()

        self.drawn_annotation = None
        self.fig.canvas.draw_idle()


class PlotAnnotator(Annotator):

    def __init__(self, annotations, fig, annmarkerfacecolor='r', annfacecolor='w', annedgecolor='k'):
        Annotator.__init__(self, annotations, fig, annmarkerfacecolor, annfacecolor, annedgecolor)

    def __call__(self, event):
        ax = event.inaxes

        axis_annotations = self.annotations[ax]

        if ax is None:
            ax = plt.gca()

        if event.name == 'button_press_event':
            click_x = event.xdata
            click_y = event.ydata

            min_idx = None
            min_dist = np.inf

            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            x_range = xlim[1] - xlim[0]
            y_range = ylim[1] - ylim[0]

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
            try:
                x, y, a = annotation
                self.draw_annotation(ax, x, y, a)
                self.shown = min_idx
            except TypeError:
                pass

        elif event.name == 'key_press_event':
            shown = self.shown
            if self.shown is None:
                return

            i, j = self.shown
            line = ax.lines[i]
            if event.key == 'left':
                if j == 0:
                    return
                x = line.get_xdata()[j - 1]
                y = line.get_ydata()[j - 1]
                try:
                    annotation = [x, y, axis_annotations[i][j - 1]]
                except IndexError:
                    annotation = [x, y, None]
                self.draw_annotation(ax, x, y, annotation)
                self.shown = (shown[0], shown[1] - 1)
            elif event.key == 'right':
                if j == line.get_xdata().size - 1:
                    return
                x = line.get_xdata()[j + 1]
                y = line.get_ydata()[j + 1]
                try:
                    annotation = [x, y, axis_annotations[i][j + 1]]
                except IndexError:
                    annotation = [x, y, None]
                self.draw_annotation(ax, x, y, annotation)
                self.shown = (shown[0], shown[1] + 1)
            elif event.key == 'escape' or event.key == 'delete':
                self.clear_annotation()

    def draw_annotation(self, ax, x, y, annotation):
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        deltax = (xlim[1] - xlim[0]) / 50
        deltay = (ylim[1] - ylim[0]) / 50

        self.clear_annotation()

        if annotation is not None:
            text = f'{x:.4f}, {y:.4f}\n{annotation}'
        else:
            text = f'{x:.4f}, {y:.4f}'

        t = ax.text(x + deltax, y + deltay, text, bbox={'facecolor': self.annfacecolor, 'edgecolor': self.annedgecolor})

        m = ax.scatter([x], [y], marker='s', c=self.annmarkerfacecolor, zorder=100)
        self.drawn_annotation = (t, m)

        ax.figure.canvas.draw_idle()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
