# annoplot
This module lets you draw clickable, interactive and annotated plots with matplotlib

## Features
The final behaviour is similar to plotting with Matlab®, you can click on the plotting area and get information about the nearest point. It is also possible to move around with arrows, provided that the mouse is inside the plotting area.

As of now it is possible to add annotations to matplotlib's `plot`, `imshow` and `hist`.

## Usage

Just import annoplot and use one of the functions

`import annoplot as aplt`

annoplot in the background just calls matplotlib standard functions, thus it's possible to pass in all arguments normally used in the default functions (as keyword arguments, positional arguments won't work).

## Examples

```python
aplt.plot(np.random.rand(1000), np.random.randn(1000), annotations=np.repeat('Point inside a useless plot', 1000), fmt='*')

# Additional customisations can then be added normally
plt.title('Useless plot')
```

![Plot example](images/plot_example.png?raw=true "plot example")
