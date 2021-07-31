# annoplot
This module lets you draw clickable, interactive and annotated plots with matplotlib

## Features
The final behaviour is similar to plotting with Matlab®, you can click on the plotting area and get the position of
the nearest point. It is also possible to move around with arrows, provided that the mouse is inside the plotting area.

In case of `plt.plot` it's also possible to add a label to each point of the Line objects created by this function.

As of now it is possible to add annotations to matplotlib's `plot`, `imshow`, `boxplot` and `hist`, but not to axes
containing a mixture of objects created using these functions.

## Usage

Just import annoplot, make your plots and then call `annotate`.

Calling `annotate` makes plots able to display the x and y location of the plotted point nearest to the click.
Accepted arguments when calling `annotate` are:
* `annotations` - valid only for Line objects, created using `plt.plot`. With this argument it's possible to add
  additional information to each point of the plots, that is then shown beneath the position.
  The annotations should be a list of lists if there is only one axis, where each inner list contains the annotations
  for the given Line, or a dict mapping each axis to its annotations, in case of multiple axes.
  If there is only one Line, it's possible to just pass a list.
* `fig` - specifying the figure to annotate. If not defined, the last one is used.
* `annmarkerfacecolor` - the face color of the marker shown over the annotated point.
* `annfacecolor` - the face color of the box shown near the annotated point and containing the location.
* `annedgecolor` - the edge color of the box shown near the annotated point and containing the location.


## Examples

```python
import numpy as np
import matplotlib.pyplot as plt
import annoplot as aplt

fig, ax = plt.subplots(2,2)
ax[0][0].plot(np.random.rand(100))
ax[0][0].plot(np.arange(0, 100, 5), np.random.rand(20) + 2)
ax[0][1].hist(np.random.randn(1000))
ax[1][0].imshow(np.random.randn(20,20))
ax[1][1].boxplot([np.random.randn(100), np.random.randn(100)])
aplt.annotate({ax[0][0]: [['First line: ' + str(i) for i in range(100)], ['Second line: ' + str(i) for i in range(20)]]})
```

![Plot example](images/plot_example.png?raw=true "plot example")
