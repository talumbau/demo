from collections import OrderedDict

import pandas as pd

from bokeh.charts import Bar, output_file, show
from bokeh.sampledata.olympics2014 import data
from bokeh.models.widgets import HBox, VBox, VBoxForm, PreText, Select
from bokeh.io import vform
from bokeh.models import Callback, ColumnDataSource, Slider
from bokeh.plotting import figure, output_file, show


df = pd.io.json.json_normalize(data['data'])

import pdb;pdb.set_trace()
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

bar = Bar(medals, countries, title="Stacked bars", stacked=True, legend=True)

show(bar)
