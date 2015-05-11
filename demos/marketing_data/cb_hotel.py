from bokeh.io import vform
from bokeh.models import Callback, ColumnDataSource, Slider
from bokeh.plotting import figure, output_file, show

import hotel_datasource

plot, source = hotel_datasource.make_usa_plot()

callback = Callback(args=dict(source=source), code="""
    var data = source.get('data');
    var f = cb_obj.get('value')
    fill = data['fill_color']
    allc = data['all_color']
    fc = data['first_color']
    sc = data['second_color']
    tc = data['third_color']
    foc = data['fourth_color']
    if (f == 4) {
        for (i = 0; i < fill.length; i++) {
            fill[i] = allc[i]
        }
    }
    if (f == 3) {
        for (i = 0; i < fill.length; i++) {
            fill[i] = fc[i]
        }
    }
    if (f == 2) {
        for (i = 0; i < fill.length; i++) {
            fill[i] = sc[i]
        }
    }
    if (f == 1) {
        for (i = 0; i < fill.length; i++) {
            fill[i] = tc[i]
        }
    }
    if (f == 0) {
        for (i = 0; i < fill.length; i++) {
            fill[i] = foc[i]
        }
    }
    source.trigger('change');
""")

slider = Slider(start=0, end=4, value=4, step=1,
                title="value", callback=callback)

layout = vform(slider, plot)

output_file("cb.html", title="callback example")
show(layout)

