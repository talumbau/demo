from collections import OrderedDict

import pandas as pd

from bokeh.charts import Bar, output_file, show
from bokeh.sampledata.olympics2014 import data
from bokeh.models.widgets import HBox, VBox, VBoxForm, PreText, Select
from bokeh.io import vform
from bokeh.models import Callback, ColumnDataSource, Slider
from bokeh.plotting import figure, output_file, show

N = 4000

factors = ["a", "b", "c", "d", "e", "f", "g", "h"]
ofactors = ["A", "B", "C", "D", "E", "F", "G", "H"]
x0 = [0, 0, 0, 0, 0, 0, 0, 0]
x =  [50, 40, 65, 10, 25, 37, 80, 60]

bsource = ColumnDataSource(data=dict(factors=factors, x=x, x0=x0, ofactors=ofactors))
#output_file("categorical.html", title="categorical.py example")

p1 = figure(title="Dot Plot", tools="resize,save", y_range=factors, x_range=[0,100])

p1.segment('x0', 'factors', 'x', 'factors', source=bsource, line_width=2, line_color="green", )
#p1.circle(x, factors, size=15, fill_color="orange", line_color="green", line_width=3, )
p1.circle('x', 'factors', source=bsource, size=15, fill_color="orange", line_color="green", line_width=3, )

factors = ["foo", "bar", "baz"]
x = ["foo", "foo", "foo", "bar", "bar", "bar", "baz", "baz", "baz"]
y = ["foo", "bar", "baz", "foo", "bar", "baz", "foo", "bar", "baz"]
colors = [
          "#0B486B", "#79BD9A", "#CFF09E",
          "#79BD9A", "#0B486B", "#79BD9A",
          "#CFF09E", "#79BD9A", "#0B486B"]
  
df = pd.io.json.json_normalize(data['data'])

# filter by countries with at least one medal and sort
df = df[df['medals.total'] > 0]
df = df.sort("medals.total", ascending=False)

# get the countries and we group the data by medal type
countries = df.abbr.values.tolist()
gold = df['medals.gold'].astype(float).values
silver = df['medals.silver'].astype(float).values
bronze = df['medals.bronze'].astype(float).values

# build a dict containing the grouped data
#medals = OrderedDict(bronze=bronze, silver=silver, gold=gold)
medals = OrderedDict(bronze=bronze)

# any of the following commented are also alid Bar inputs
#medals = pd.DataFrame(medals)
#medals = list(medals.values())

output_file("barc.html")

callback = Callback(args=dict(source=bsource), code="""
    var data = source.get('data');
    var f = cb_obj.get('value')
    fac = data['factors']
    ofac = data['ofactors']
    for (i = 0; i < fac.length; i++) {
        fac[i] = ofac[i]
    }
    source.trigger('change');
""")

slider = Slider(start=-2, end=2, value=1, step=.1,
                title="value", callback=callback)

#layout = vform(slider, plot)
layout = vform(slider, p1)

output_file("cb_bar.html", title="callback example")
show(layout)

