from bokeh.io import vform
from bokeh.models import Callback, ColumnDataSource, Slider
from bokeh.plotting import figure, output_file, show

x = list(range(-50, 51))
y = list(x)

source = ColumnDataSource(data=dict(x=x, y=y))

plot = figure(y_range=(-100, 100), plot_width=400, plot_height=400)
plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

callback = Callback(args=dict(source=source), code="""
    var data = source.get('data');
    var f = cb_obj.get('value')
    x = data['x']
    y = data['y']
    for (i = 0; i < x.length; i++) {
        y[i] = f * x[i]
    }
    source.trigger('change');
""")

slider = Slider(start=-2, end=2, value=1, step=.1,
                title="value", callback=callback)

layout = vform(slider, plot)

output_file("cb.html", title="callback example")
show(layout)

