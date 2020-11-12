# annoplot
This module lets you draw clickable, interactive and annotated plots with matplotlib

## Features
The final behaviour is similar to plotting with Matlab®, you can click on the plotting area and get information about the nearest point. It is also possible to move around with arrows, provided that the mouse is inside the plotting area.

As of now it is possible to add annotations to matplotlib's `plot`, `imshow`, `boxplot` and `hist`.

## Usage

Just import annoplot, make your plots and then call `annotate`.

`annotate` will display the x and y location of the plotted point nearest to the click. In case of `plt.plot` it's possible to provide additional information via the
argument `annotations`: The annotations should be a list of lists if there is only on axis, where each inner list contains the annotations for the given line, or a dict mapping each axis to its annotations, in case of multiple axes.
If there is only one line it's possible to just provide a list.

## Examples

```python
import annoplot as aplt

fig, ax = plt.subplots(2,2)
ax[0][0].plot(np.random.rand(100))
ax[0][0].plot(np.arange(0, 100, 5), np.random.rand(20) + 2)
ax[0][1].hist(np.random.randn(1000))
ax[1][0].imshow(np.random.randn(20,20))
ax[1][0].set_xticklabels(np.random.randint(0, 100, 100))
ax[1][1].boxplot([np.random.randn(100), np.random.randn(100)])
aplt.annotate({ax[0][0]: [['First line: ' + str(i) for i in range(100)], ['Second line: ' + str(i) for i in range(20)]]})
```

![Plot example](images/plot_example.png?raw=true "plot example")
