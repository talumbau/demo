from collections import OrderedDict


import pandas as pd
import numpy as np

from bokeh.charts import Bar, output_file, show
from bokeh.sampledata.olympics2014 import data
from bokeh.models.widgets import HBox, VBox, VBoxForm, PreText, Select
from bokeh.models import ColumnDataSource, Slider
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

rangenames = ["lt100", "lt200", "lt300", 
          "lt400", "lt500", "lt600", "lt700", "lt800", "lt900", 
          "lt1000", "lt1100", "lt1200", "lt1300", "lt1400", "lt1500", 
          "lt1600", "lt1700", "lt1800", "lt1900", "lt2000", "lt2100", 
          "lt2200", "lt2300", "lt2400", "lt2500", "lt2600", "lt2700", 
          "lt2800", "lt2900", "lt3000", "lt3100", "lt3200", "lt3300", 
          "lt3400", "lt3500", "lt3600", "lt3700", "lt3800", "lt3900", 
          "lt4000", ">= $4000"]


gold = df['medals.gold'].astype(float).values
silver = df['medals.silver'].astype(float).values
bronze = df['medals.bronze'].astype(float).values

# build a dict containing the grouped data
medals = OrderedDict(bronze=bronze, silver=silver, gold=gold)
#medals = OrderedDict(bronze=bronze)

b2p = shoes_func.get_brands_to_prices()
"""b2p = { 'aaa': [50.0, 250.0, 550.0],
        'bbb': [150.0, 350.0, 850.0],
        'ccc': [750.0, 1350.0, 350.0]}"""

def make_row(idxs, _len):
    x = np.zeros(_len)
    for indx in idxs:
        try:
            x[indx] = 1
        except IndexError:
            import pdb;pdb.set_trace()
            print "what?"
    return x


just_prices = [x for x in itertools.chain.from_iterable(b2p.values())]
bins = np.arange(0.0, 4000, 100)
bins2 = np.concatenate((bins, np.array([8000.0])))
inds = np.digitize(just_prices, bins)
stacks = np.bincount(inds)
b2p_stacked = { k: make_row(np.digitize(v, bins), len(bins2)) for k,v in b2p.iteritems()}
b2p_smaller = {}

for count, k in enumerate(b2p_stacked):
    b2p_smaller[k] = b2p_stacked[k]
    if count > 25:
        break
# any of the following commented are also alid Bar inputs
#medals = pd.DataFrame(medals)
#medals = list(medals.values())

output_file("lux.html")

#bar = Bar(medals, countries, title="Stacked bars", stacked=True, legend=True)
#shoes = OrderedDict(shoes=stacks)
#bar = Bar(shoes, ranges, title="Price Distribution", stacked=True, legend=True, width=1100, height=700)
bar = Bar(b2p_smaller, ranges, title="Price Distribution", stacked=True, width=1100, height=700,
          legend="top_right")

show(bar)
