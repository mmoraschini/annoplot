from typing import Optional, Union, Dict, List, Any
import datetime
import collections

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.axis import Axis


AnnotationsType = Union[list, List[list], dict]


def _distance(x1: float, x2: float, y1: float, y2: float) -> float:
    """
    return the Manhattan _distance between two points

    @param x1: x position of point 1
    @param x2: x position of point 2
    @param y1: y position of point 1
    @param y2: y position of point 2
    @return: a float with the Manhattan distance
    """

    return abs(x1 - x2) + abs(y1 - y2)


def annotate(annotations: Optional[AnnotationsType] = None, fig: Optional[Figure] = None,
             annmarkerfacecolor: str = 'r', annfacecolor: str = 'w', annedgecolor: str = 'k'):
    """
    Connects an Annotator to the given figure to show the given annotations

    @param annotations: a list, a list of list or a dict containing the annotations. A list of lists is used if there
        are multiple plots on the same axis, a dictionary if there are more axes. The keys of the dictionary must be the
        axes and the values the annotations.
    @param fig: the figure on which to show annotations. If None takes the last one opened. If there are no open
        figures raises an error.
    @param annmarkerfacecolor: the colour of the marker
    @param annfacecolor: the background colour of the box
    @param annedgecolor: the edge colour of the box
    """
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
            for ax in axes:
                if ax not in annotations:
                    annotations[ax] = []

    antr = Annotator(annotations, fig, annmarkerfacecolor, annfacecolor, annedgecolor)
    fig.canvas.mpl_connect('button_press_event', antr)
    fig.canvas.mpl_connect('key_press_event', antr)


def _is_arraylike(x: Any) -> bool:

    if isinstance(x, (list, tuple, np.ndarray)):
        return True
    else:
        return False


class Annotator:
    """
    A class to show an annotation next to the point of a plot nearest to the click and move around with arrows.

    Right: next point
    Left: previous point
    Esc, Del: clear the current annotation box

    @param annotations: a list, a list of list or a dict containing the annotations. A list of lists is used if
        there are multiple plots on the same axis, a dictionary if there are more axes. The keys of the dictionary
        must be the axes and the values the annotations
    @param fig: the figure on which to show annotations
    @param annmarkerfacecolor: the colour of the marker
    @param annfacecolor: the background colour of the box
    @param annedgecolor: the edge colour of the box
    """
    def __init__(self, annotations: AnnotationsType, fig: Figure,
                 annmarkerfacecolor: str, annfacecolor: str, annedgecolor: str):
        self.annotations = annotations
        self.fig = fig
        self.annmarkerfacecolor = annmarkerfacecolor
        self.annfacecolor = annfacecolor
        self.annedgecolor = annedgecolor

        self.drawn_annotation: Dict[Axis, Union[None, tuple]] = {}
        self.shown: Dict[Axis, Union[None, tuple]] = {}
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

        if len(ax.lines) > 0 and len(ax.images) == 0 and len(ax.patches) == 0:
            # Annotations must be enclosed in a list so that there can be more annotated lines
            arraylike_check = [_is_arraylike(x) for x in self.annotations[ax]]
            if not np.all(arraylike_check):
                self.annotations[ax] = [self.annotations[ax]]
            self._manage_plot(event, arguments, 'line')
        elif len(ax.lines) == 0 and len(ax.images) > 0 and len(ax.patches) == 0:
            self._manage_plot(event, arguments, 'image')
        elif len(ax.lines) == 0 and len(ax.images) == 0 and len(ax.patches) > 0:
            self._manage_plot(event, arguments, 'patch')
        else:
            raise (RuntimeError('Annotations can only be added to an Axis that contains Lines, Images, '
                                'Histograms, Boxplots but not a mixture of them'))

    def _manage_plot(self, event, arguments, plot_type):

        ax, click_x, click_y, x_range, y_range = arguments

        if event.name == 'button_press_event':
            chosen_idx = None
            annotation = None
            data = self._get_iterable_data(ax, plot_type)
            if plot_type == 'image':
                click_x = np.round(click_x).astype(int)
                click_y = np.round(click_y).astype(int)
                chosen_idx = (click_x, click_y)
                annotation = [click_x, click_y, None]
            else:
                min_dist = np.inf
                for i, d in enumerate(data):
                    xdata = d[0]
                    ydata = d[1]
                    for j in range(len(xdata)):
                        x = xdata[j]
                        y = ydata[j]
                        if isinstance(x, datetime.datetime):
                            x = mdates.date2num(x)
                        if isinstance(y, datetime.datetime):
                            y = mdates.date2num(y)

                        dist = _distance(x / x_range, click_x / x_range, y / y_range, click_y / y_range)
                        if dist < min_dist:
                            try:
                                annotation = [x, y, self.annotations[ax][i][j]]
                            except IndexError:
                                annotation = [x, y, None]
                            min_dist = dist
                            chosen_idx = (i, j)

            x, y, a = annotation
            self._draw_annotation(ax, x, y, a)
            self.shown[ax] = chosen_idx

        elif event.name == 'key_press_event':
            if self.shown[ax] is None:
                return

            i, j = self.shown[ax]
            data = self._get_iterable_data(ax, plot_type)

            res = self._manage_key_press(ax, data, i, j, event.key, plot_type)

            if res is not None:
                x, y, a = res
                self._draw_annotation(ax, x, y, a)

    def _manage_key_press(self, ax, data, i, j, key, plot_type) -> Union[None, tuple]:
        x, y, a = (None, None, None)
        if key == 'left':
            if plot_type == 'image':
                if i != 0:
                    x, y, a = (i - 1, j, None)
                    self.shown[ax] = (self.shown[ax][0] - 1, self.shown[ax][1])
                else:
                    return None
            else:
                if j != 0:
                    x = data[i][0][j - 1]
                    y = data[i][1][j - 1]
                    try:
                        a = self.annotations[ax][i][j - 1]
                    except IndexError:
                        a = None
                    self.shown[ax] = (self.shown[ax][0], self.shown[ax][1] - 1)
                else:
                    return None
        elif key == 'right':
            if plot_type == 'image':
                if i < data[0][1] - 1:  # max extent of horizontal axis
                    x, y, a = (i + 1, j, None)
                    self.shown[ax] = (self.shown[ax][0] + 1, self.shown[ax][1])
                else:
                    return None
            else:
                if j != len(data[i][0]) - 1:
                    x = data[i][0][j + 1]
                    y = data[i][1][j + 1]
                    try:
                        a = self.annotations[ax][i][j + 1]
                    except IndexError:
                        a = None
                    self.shown[ax] = (self.shown[ax][0], self.shown[ax][1] + 1)
                else:
                    return None
        elif key == 'up':
            if plot_type == 'image':
                if j != 0:
                    x, y, a = (i, j - 1, None)
                    self.shown[ax] = (self.shown[ax][0], self.shown[ax][1] - 1)
                else:
                    return None
            else:
                return None
        elif key == 'down':
            if plot_type == 'image':
                if j < data[1][0] - 1:  # max extent of vertical axis
                    x, y, a = (i, j + 1, None)
                    self.shown[ax] = (self.shown[ax][0], self.shown[ax][1] + 1)
                else:
                    return None
            else:
                return None
        elif key == 'escape' or key == 'backspace':
            self._clear_annotation(ax)
            return None

        return x, y, a

    def _get_iterable_data(self, ax, plot_type):

        data = None
        if plot_type == 'line':
            lines = ax.lines
            data = [(line.get_xdata(), line.get_ydata()) for line in lines]
        elif plot_type == 'image':
            xdata = ax.get_xlim()
            ydata = ax.get_ylim()
            data = (xdata, ydata)
        elif plot_type == 'patch':
            n = len(ax.patches)
            xdata = np.empty(n, dtype=float)
            ydata = np.empty(n, dtype=float)
            for i, p in enumerate(ax.patches):
                bbox = p.get_bbox()
                xdata[i] = (bbox.xmin + bbox.xmax) / 2
                ydata[i] = bbox.ymax  # (bbox.ymin + bbox.ymax) / 2
            data = [(xdata, ydata)]

        return data

    def _draw_annotation(self, ax, x, y, annotation):
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        deltax = abs(xlim[1] - xlim[0]) / 50
        deltay = abs(ylim[1] - ylim[0]) / 50

        bkup_shown = self.shown[ax]
        self._clear_annotation(ax)
        self.shown[ax] = bkup_shown

        if annotation is not None:
            text = '{:.4f}, {:.4f}\n{}'.format(x, y, annotation)
        else:
            text = '{:.4f}, {:.4f}'.format(x, y)

        t = ax.text(x + deltax, y + deltay, text,
                    bbox={'facecolor': self.annfacecolor, 'edgecolor': self.annedgecolor})

        bb = t.get_window_extent(renderer=self.fig.canvas.renderer).transformed(ax.transData.inverted())

        change = False

        if ylim[0] > ylim[1]:
            vlim = (ylim[1], ylim[0])
        else:
            vlim = ylim

        # Adjust annotation box so that it does not go past the borders
        final_pos_x = x + deltax
        if final_pos_x + bb.width > xlim[1]:
            final_pos_x -= (final_pos_x + bb.width - xlim[1])
            change = True
        final_pos_y = y + deltay
        if final_pos_y + bb.height > vlim[1]:
            final_pos_y -= (final_pos_y + bb.height - vlim[1])
            change = True

        if change:
            t.remove()
            t = ax.text(final_pos_x, final_pos_y, text,
                        bbox={'facecolor': self.annfacecolor, 'edgecolor': self.annedgecolor})

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
