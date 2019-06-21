from abc import ABC, abstractmethod

import numpy as np
import matplotlib.pyplot as plt

class Annotator(ABC):
    def __init__(self, ax, annmarkerfacecolor, annfacecolor, annedgecolor):
        self.drawn_annotations = {}
        
        if ax is None:
            self.ax = plt.gca()
        else:
            self.ax = ax
        
        self.annmarkerfacecolor = annmarkerfacecolor
        self.annfacecolor = annfacecolor
        self.annedgecolor = annedgecolor
    
    @abstractmethod
    def clear_shown_element(self):
        pass
    
    def clear_annotations(self):
        if len(self.drawn_annotations) > 0:
            for k in list(self.drawn_annotations.keys()):
                self.drawn_annotations[k][0].remove()
                self.drawn_annotations[k][1].remove()
                self.ax.figure.canvas.draw_idle()
                del self.drawn_annotations[k]
                self.clear_shown_element()

class ImAnnotator(Annotator):

    def __init__(self, im, ax=None, annmarkerfacecolor='r', annfacecolor='w', annedgecolor='k'):
        Annotator.__init__(self, ax, annmarkerfacecolor, annfacecolor, annedgecolor)
        self.im = im
        
        self.shown_pnt = [None, None]
    
    def __call__(self, event):        
        if event.inaxes:
            if event.name == 'button_press_event':
                clickX = event.xdata
                clickY = event.ydata
                if (self.ax is None) or (self.ax is event.inaxes):
                    self.draw_annotation(event.inaxes, clickX, clickY)
            
            elif event.name == 'key_press_event' and self.ax is event.inaxes:
                if np.all(self.shown_pnt) is None:
                    return
                
                if event.key == 'left':
                    if self.shown_pnt[0] == 0:
                        return
                    
                    self.draw_annotation(event.inaxes, self.shown_pnt[0]-1, self.shown_pnt[1])
                elif event.key == 'right':
                    if self.shown_pnt[0] == self.im.shape[1]-1:
                        return
                    
                    self.draw_annotation(event.inaxes, self.shown_pnt[0]+1, self.shown_pnt[1])
                elif event.key == 'up':
                    if self.shown_pnt[1] == 0:
                        return
                    
                    self.draw_annotation(event.inaxes, self.shown_pnt[0], self.shown_pnt[1]-1)
                elif event.key == 'down':
                    if self.shown_pnt[1] == self.im.shape[0]-1:
                        return
                    
                    self.draw_annotation(event.inaxes, self.shown_pnt[0], self.shown_pnt[1]+1)
                elif event.key == 'escape' or event.key == 'delete':
                    self.clear_annotations()
    
    def draw_annotation(self, ax, x, y):
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        deltax = (xlim[1] - xlim[0]) / 50
        deltay = (ylim[1] - ylim[0]) / 50
        
        xlb = ax.get_xticklabels()
        ylb = ax.get_yticklabels()
        
        xrnd = np.round(x).astype(int)
        yrnd = np.round(y).astype(int)
                
        (xlb_val, ylb_val) = (None, None)
        for i in iter(xlb):
            for j in iter(ylb):
                if i.get_position()[0] == xrnd and j.get_position()[1] == yrnd:
                    (xlb_val, ylb_val) = (i, j)
                    break
        
        if xlb_val is None or ylb_val is None:
            xtext = str(xrnd)
            ytext = str(yrnd)
            
            xidx = xrnd
            yidx = yrnd
        else:
            xtext = xlb_val.get_text()
            ytext = ylb_val.get_text()
            
            xidx = int(xlb_val.get_position()[0])
            yidx = int(ylb_val.get_position()[1])
        
        value = self.im[yidx, xidx]
        
        self.clear_annotations()
        
        t = ax.text(xrnd+deltax, yrnd+deltay,
                    '{}, {}\n{:.4f}'.format(ytext, xtext, value),
                    bbox={'facecolor':self.annfacecolor, 'edgecolor':self.annedgecolor}, zorder=100)
        m = ax.scatter([xrnd], [yrnd], marker='s', c=self.annmarkerfacecolor, zorder=100)
        self.drawn_annotations[(xrnd, yrnd)] = (t, m)
        self.ax.figure.canvas.draw_idle()
        
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        
        self.shown_pnt = [xrnd, yrnd]
    
    def clear_shown_element(self):
        self.shown_pnt = [None, None]

class PlotAnnotator(Annotator):

    def __init__(self, xdata, ydata=None, annotations=None, ax=None, annmarkerfacecolor='r', annfacecolor='w', annedgecolor='k'):
        Annotator.__init__(self, ax, annmarkerfacecolor, annfacecolor, annedgecolor)
        
        if xdata.ndim == 1 and ydata is None:
            ydata = xdata
            xdata = np.arange(len(ydata))
        
        if annotations is None:
            annotations = ['' for i in range(len(xdata))]
            for i in range(len(xdata)):
                annotations[i] = '{0:.4f}, {1:.4f}'.format(xdata[i], ydata[i])
        
        self.data = list(zip(xdata, ydata, annotations))
        
        self.shown_idx = -1

    def distance(self, x1, x2, y1, y2):
        """
        return the distance between two points
        """
#        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        return abs(x1 - x2) + abs(y1 - y2)

    def __call__(self, event):

        if event.inaxes:
            if event.name == 'button_press_event':
                clickX = event.xdata
                clickY = event.ydata
                if (self.ax is None) or (self.ax is event.inaxes):
                    i_min = 0
                    min_dist = np.inf
                    i = 0
                    xlim = self.ax.get_xlim()
                    ylim = self.ax.get_ylim()
                    x_range = xlim[1] - xlim[0]
                    y_range = ylim[1] - ylim[0]
                    for x, y, a in self.data:
                        dist = self.distance(x/x_range, clickX/x_range, y/y_range, clickY/y_range)
                        if dist < min_dist:
                            annotation = (x, y, a)
                            min_dist = dist
                            i_min = i
                        i+=1
                    
                    x,y,a = annotation
                    self.draw_annotation(event.inaxes, x, y, a)
                    self.shown_idx = i_min
                                
            elif event.name == 'key_press_event' and self.ax is event.inaxes:
                shown = self.shown_idx
                if self.shown_idx == -1:
                    return
                
                if event.key == 'left':
                    if self.shown_idx == 0:
                        return
                    x, y, a = self.data[self.shown_idx - 1]
                    self.draw_annotation(event.inaxes, x, y, a)
                    self.shown_idx = shown-1
                elif event.key == 'right':
                    if self.shown_idx == len(self.data)-1:
                        return
                    x, y, a = self.data[self.shown_idx + 1]
                    self.draw_annotation(event.inaxes, x, y, a)
                    self.shown_idx = shown+1
                elif event.key == 'escape' or event.key == 'delete':
                    self.clear_annotations()
    
    def draw_annotation(self, ax, x, y, annotation):
        
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        deltax = (xlim[1] - xlim[0]) / 50
        deltay = (ylim[1] - ylim[0]) / 50
        
        self.clear_annotations()
        
        t = ax.text(x+deltax, y+deltay, '{}'.format(annotation),
                    bbox={'facecolor':self.annfacecolor, 'edgecolor':self.annedgecolor})
        m = ax.scatter([x], [y], marker='s', c=self.annmarkerfacecolor, zorder=100)
        self.drawn_annotations[(x, y)] = (t, m)
        self.ax.figure.canvas.draw_idle()
        
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    
    def clear_shown_element(self):
        self.shown_idx = -1

def close_all():
    plt.close('all')

def _manage_subplots(fig, subplotargs):
    if fig is None:
        fig, ax = plt.subplots()
    else:
        if subplotargs is None:
            ax = plt.subplot()
        elif type(subplotargs) == int:
            ax = plt.subplot(subplotargs)
        else:
            ax = plt.subplot(*subplotargs)
    
    return fig, ax

def _manage_kwargs(kwargs):
    extra_args = {}
    available_args = ['annmarkerfacecolor', 'annfacecolor', 'annedgecolor']
    for arg in available_args:
        if arg in kwargs:
            extra_args[arg] = kwargs[arg]
            del kwargs[arg]
    
    return extra_args
    
def plot(x, y=None, annotations=None, fig=None, subplotargs=None, plotstyle=None, **kwargs):
    """
    Shows a plot and adds the annotations. Available kwargs are those
    accepted by matplotlib.pyplot.plot plus 'annmarkerfacecolor', annfacecolor' and
    'annedgecolor', used to style drawn annotations.
    
    -- inputs
    x: coordinates on the x-axis
    y: coordinates on the y-axis
    annotations: additional annotations to show
    fig: if None generates a new figure
    subplotargs: Either a 3-digit integer or three separate integers describing
        the position of the subplot. See plt.subplot for more info
    
    -- returns
    fig: figure generated by plt.subplots()
    ax: axes generated by plt.subplots()
    """
    if y is None:
        y = np.arange(len(x))
    
    fig, ax = _manage_subplots(fig, subplotargs)
    
    annotation_strings = ['' for i in range(len(x))]
    for i in range(len(x)):
        annotation_strings[i] = '{:.4f}, {:.4f}'.format(x[i], y[i])
        if annotations is not None:
            annotation_strings[i] = annotation_strings[i] + '\n{}'.format(annotations[i])
    
    extra_args = _manage_kwargs(kwargs)
    
    antr = PlotAnnotator(x, y, annotation_strings, ax=ax, **extra_args)
    fig.canvas.mpl_connect('button_press_event', antr)
    fig.canvas.mpl_connect('key_press_event', antr)
    if plotstyle is not None:
        plt.plot(x, y, plotstyle, **kwargs)
    else:
        plt.plot(x, y,**kwargs)
    
    return fig, ax

def imshow(im, fig=None, subplotargs=None, **kwargs):
    """
    Shows an image and adds the annotations. Available kwargs are those
    accepted by matplotlib.pyplot.imshow plus 'annmarkerfacecolor', 'annfacecolor' and
    'annedgecolor', used to style drawn annotations.
    
    -- inputs
    im: pixel values to show
    fig: if None generates a new figure
    subplotargs: Either a 3-digit integer or three separate integers describing
        the position of the subplot. See plt.subplot for more info
    
    -- returns
    fig: figure generated by plt.subplots()
    ax: axes generated by plt.subplots()
    """
    
    fig, ax = _manage_subplots(fig, subplotargs)
    
    extra_args = _manage_kwargs(kwargs)
    
    antr = ImAnnotator(im, ax=ax, **extra_args)
    fig.canvas.mpl_connect('button_press_event', antr)
    fig.canvas.mpl_connect('key_press_event', antr)
    plt.imshow(im,**kwargs)
    
    return fig, ax

def hist(x, fig=None, subplotargs=None, **kwargs):
    """
    Shows a histogram and adds the annotations. Available kwargs are those
    accepted by matplotlib.pyplot.hist plus 'annmarkerfacecolor', 'annfacecolor' and
    'annedgecolor', used to style drawn annotations.
    
    -- inputs
    x: input values
    fig: if None generates a new figure
    subplotargs: Either a 3-digit integer or three separate integers describing
        the position of the subplot. See plt.subplot for more info
    
    -- returns
    fig: figure generated by plt.subplots()
    ax: axes generated by plt.subplots()
    """
    
    fig, ax = _manage_subplots(fig, subplotargs)
    
    extra_args = _manage_kwargs(kwargs)
    
    vals, edges, _ = plt.hist(x, **kwargs)
    bin_centres = np.zeros(vals.size)
    for i in range(len(edges)-1):
        bin_centres[i] = (edges[i] + edges[i+1]) / 2
    
    annotation_strings = ['' for i in range(len(vals))]
    for i in range(len(vals)):
        annotation_strings[i] = 'edges: {:.4f}, {:.4f}\ncount:{:.0f}'.format(edges[i], edges[i+1], vals[i])
    
    antr = PlotAnnotator(bin_centres, vals, annotation_strings, ax=ax, **extra_args)
    fig.canvas.mpl_connect('button_press_event', antr)
    fig.canvas.mpl_connect('key_press_event', antr)
    
    return fig, ax
