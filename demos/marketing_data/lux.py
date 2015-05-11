from collections import OrderedDict


import pandas as pd
import numpy as np

from bokeh.charts import Bar, output_file, show
from bokeh.sampledata.olympics2014 import data
from bokeh.models.widgets import HBox, VBox, VBoxForm, PreText, Select
from bokeh.io import vform
from bokeh.models import Callback, ColumnDataSource, Slider
from bokeh.plotting import figure, output_file, show
import shoes_func
import itertools


df = pd.io.json.json_normalize(data['data'])

# filter by countries with at least one medal and sort
df = df[df['medals.total'] > 0]
df = df.sort("medals.total", ascending=False)

# get the countries and we group the data by medal type
countries = df.abbr.values.tolist()
ranges = ["< $100", "< $200", "< $300", 
          "< $400", "< $500", "< $600", "< $700", "< $800", "< $900", 
          "< $1000", "< $1100", "< $1200", "< $1300", "< $1400", "< $1500", 
          "< $1600", "< $1700", "< $1800", "< $1900", "< $2000", "< $2100", 
          "< $2200", "< $2300", "< $2400", "< $2500", "< $2600", "< $2700", 
          "< $2800", "< $2900", "< $3000", "< $3100", "< $3200", "< $3300", 
          "< $3400", "< $3500", "< $3600", "< $3700", "< $3800", "< $3900", 
          "< $4000", ">= $4000"]
gold = df['medals.gold'].astype(float).values
silver = df['medals.silver'].astype(float).values
bronze = df['medals.bronze'].astype(float).values

# build a dict containing the grouped data
#medals = OrderedDict(bronze=bronze, silver=silver, gold=gold)
medals = OrderedDict(bronze=bronze)

b2p = shoes_func.get_brands_to_prices()
just_prices = [x for x in itertools.chain.from_iterable(b2p.values())]
bins = np.arange(0.0, 4000, 100)
bins2 = np.concatenate((bins, np.array([8000.0])))
inds = np.digitize(just_prices, bins)
stacks = np.bincount(inds)
# any of the following commented are also alid Bar inputs
#medals = pd.DataFrame(medals)
#medals = list(medals.values())

output_file("lux.html")

#bar = Bar(medals, countries, title="Stacked bars", stacked=True, legend=True)
shoes = OrderedDict(shoes=stacks)
bar = Bar(shoes, ranges, title="Price Distribution", stacked=True, legend=True, width=1100, height=700)

show(bar)
