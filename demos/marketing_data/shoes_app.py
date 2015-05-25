"""
This file demonstrates a bokeh applet, which can either be viewed
directly on a bokeh-server, or embedded into a flask application.
See the README.md file in this directory for instructions on running.
"""

import logging
import random
import bokeh

logging.basicConfig(level=logging.DEBUG)

from os import listdir
from os.path import dirname, join, splitext

import numpy as np
from numpy import pi
import pandas as pd
import shoes_func

from bokeh.models import ColumnDataSource, Plot, HoverTool, TapTool
from bokeh.plotting import figure, curdoc
from bokeh.charts import Bar, output_file, show, Histogram
from bokeh.properties import String, Instance
from bokeh.server.app import bokeh_app
from bokeh.server.utils.plugins import object_page
from bokeh.models.widgets import HBox, VBox, VBoxForm, PreText, Select

ranges = ["< $100", "< $200", "< $300", 
          "< $400", "< $500", "< $600", "< $700", "< $800", "< $900", 
          "< $1000", "< $1100", "< $1200", "< $1300", "< $1400", "< $1500", 
          "< $1600", "< $1700", "< $1800", "< $1900", "< $2000", "< $2100", 
          "< $2200", "< $2300", "< $2400", "< $2500", "< $2600", "< $2700", 
          "< $2800", "< $2900", "< $3000", "< $3100", "< $3200", "< $3300", 
          "< $3400", "< $3500", "< $3600", "< $3700", "< $3800", "< $3900", 
          "< $4000", ">= $4000"]

MAX_IDX = 41

orig_order = list(ranges)
ranges.reverse()

num_slots = len(ranges)


_shoedf = shoes_func.get_all_shoes()
def get_shoe_data():
    #b2p = shoes_func.get_brands_to_prices()
    b2p = shoes_func.make_brands_to_prices(_shoedf)
    #b2p_small = {}
    #for count, k in zip(range(0,30), b2p):
        #b2p_small[k] = b2p[k]
    return b2p

b2p = get_shoe_data()
brands = [k for k in zip(range(0,20), b2p.keys())]

idx = (_shoedf['price'] + 100)//100
idx = [int(x) + 1 for x in idx]
counts = [0] * len(ranges)
xvals = []
yvals = []
xcat = []
brand_y = [0.0] * len(_shoedf['price'])
rightvals = []
tops = []
bottoms = []
fills = []
height = [0.5] * len(_shoedf['price'])
width = [0.5] * len(_shoedf['price'])

brand_aves = shoes_func.average_price_per_brand(b2p)
splitters = [100, 250, 300, 500, 750, 900, 1400, 1800, 2000, 3000, 9999]
groups = shoes_func.split_on_prices(brand_aves, splitters)
brand_to_color = shoes_func.make_brand_to_color(groups)

for i in _shoedf.index:
    ans = _shoedf.ix[i]
    #idx = int(ans['price'] + 100)//100 + 1
    idx = (num_slots - 1) - int(ans['price'] + 100)//100 + 1
    print "idx is ", idx
    print "price is ", ans['price']
    #Categorical stuff
    #xcat.append(ranges[idx-2])
    xcat.append(ranges[idx])
    yvals.append(counts[idx] - 0.5*counts[idx])

    #quad stuff
    xvals.append(idx - 0.25)
    rightvals.append(idx + 0.25)
    bottoms.append(counts[idx]/2)
    tops.append(counts[idx] + 0.5)
    counts[idx] = counts[idx] + 1
    fills.append(brand_to_color[ans['brand']])

_shoedf['xvals'] = xvals
_shoedf['xcat'] = xcat
_shoedf['rightvals'] = rightvals
_shoedf['bottoms'] = bottoms
_shoedf['tops'] = tops
_shoedf['fills'] = fills
_shoedf['yvals'] = yvals
_shoedf['height'] = height
_shoedf['width'] = width
_shoedf['brand_y'] = brand_y


def make_row(idxs, _len):
    x = np.zeros(_len)
    for indx in idxs:
        try:
            x[indx] = 1
        except IndexError:
            import pdb;pdb.set_trace()
            print "what?"
    return x

class ShoeApp(VBox):
    extra_generated_classes = [["ShoeApp", "ShoeApp", "VBox"]]
    jsmodel = "VBox"

    # plots
    plot = Instance(Plot)
    brand_plot = Instance(Plot)
    # data source
    source = Instance(ColumnDataSource)
    brand_source = Instance(ColumnDataSource)

    # layout boxes
    totalbox = Instance(HBox)

    def __init__(self, *args, **kwargs):
        super(ShoeApp, self).__init__(*args, **kwargs)

    @classmethod
    def create(cls):
        """
        This function is called once, and is responsible for
        creating all objects (plots, datasources, etc)
        """
        # create layout widgets
        obj = cls()
        obj.totalbox = HBox()

        obj.make_source()
        # outputs
        obj.make_better_plots()

        # layout
        obj.set_children()
        return obj


    def make_source(self):
        self.source = ColumnDataSource(data=self.df)
        self.make_brand_source()

    def make_brand_source(self):
        self.brand_source = ColumnDataSource(data=self.brand_df)

    def configure_brand_source(self, min_idx=0, max_idx=MAX_IDX):
        bdf = self.brand_df
        min_idx, max_idx = shoes_func.min_max_range(ranges, bdf['price'])
        counts = [0] * (max_idx - min_idx + 1)
        import pdb;pdb.set_trace()
        for i in bdf.index:
            ans = bdf.ix[i]
            #idx = int(ans['price'] + 100)//100 + 1
            idx = int(ans['price']//100)
            print "idx is ", idx
            print "price is ", ans['price']
            #Categorical stuff
            #xcat.append(ranges[idx-2])
            _shoedf.loc[i, 'brand_y'] = (counts[idx - min_idx] - 0.5*counts[idx - min_idx])
            counts[idx - min_idx] = counts[idx - min_idx] + 1
            #quad stuff
            #xvals.append(idx - 0.25)
            #rightvals.append(idx + 0.25)
            #bottoms.append(counts[idx]/2)
            #tops.append(counts[idx] + 0.5)
            #fills.append(brand_to_color[ans['brand']])



    def make_better_plots(self):

        TOOLS = "box_select,lasso_select"
        tooltips = "<span class='tooltip-text'>Name: @name</span>\n<br>"
        tooltips += "<span class='tooltip-text'>Brand: @brand</span>\n<br>"
        tooltips += "<span class='tooltip-text'>Price: @price</span>\n<br>"
        #hover = HoverTool(tooltips="@num_reviews")
        #hover = HoverTool(tooltips="@names")
        hover = HoverTool(tooltips=tooltips)
        tap = TapTool()

        #p = figure(tools=TOOLS, width=1100, height=700, x_range=x_rr, y_range=y_rr, title="Price Distribution")
        #p = figure(tools=TOOLS, width=1100, height=700, title="Price Distribution")
        #p = figure(tools=TOOLS, width=1100, height=700, x_range=ranges, title="Price Distribution", angle=pi/4)
        #p = figure(tools=TOOLS, width=1100, height=700, x_range=ranges, title="Price Distribution")
        p = figure(tools=TOOLS, width=600, height=1000, y_range=ranges, title="Price Distribution")
        p.yaxis.major_label_orientation = pi/4

        #p.quad(left='xvals', right='rightvals', top='tops', bottom='bottoms', color='fills', source=self.dfsource)
        #p.rect(x='xcat', y='yvals', width='width', height='height', color='fills', source=self.source)
        p.rect(x='yvals', y='xcat', width='width', height='height', color='fills', source=self.source)
        p.add_tools(hover, tap)

        self.plot = p
        self.make_brand_plot()

    def make_brand_plot(self, min_idx=0, max_idx=MAX_IDX):

        import pdb;pdb.set_trace()
        TOOLS = "box_select,lasso_select"
        tooltips = "<span class='tooltip-text'>Name: @name</span>\n<br>"
        tooltips += "<span class='tooltip-text'>Brand: @brand</span>\n<br>"
        tooltips += "<span class='tooltip-text'>Price: @price</span>\n<br>"
        #hover = HoverTool(tooltips="@num_reviews")
        #hover = HoverTool(tooltips="@names")
        hover = HoverTool(tooltips=tooltips)

        #p = figure(tools=TOOLS, width=1100, height=700, x_range=x_rr, y_range=y_rr, title="Price Distribution")
        #p = figure(tools=TOOLS, width=1100, height=700, title="Price Distribution")
        #p = figure(tools=TOOLS, width=1100, height=700, x_range=ranges, title="Price Distribution", angle=pi/4)
        bdf = self.brand_df
        if len(bdf) > 0:
            title = "Brand: " + self.brand_df['brand'].values[0]
        else:
            title = ""
        brand_ranges = orig_order[min_idx:max_idx]
        p = figure(tools=TOOLS, width=400, height=400, x_range=brand_ranges, title=title)
        p.xaxis.major_label_orientation = pi/4

        #p.quad(left='xvals', right='rightvals', top='tops', bottom='bottoms', color='fills', source=self.dfsource)
        p.rect(x='xcat', y='brand_y', width='width', height='height', color='fills', source=self.brand_source)
        p.add_tools(hover)

        self.brand_plot = p


    def set_children(self):
        self.children = [self.totalbox]
        self.totalbox.children = [self.plot, self.brand_plot]
        #self.totalbox.children = [self.mainrow, self.bottomrow]
        #self.mainrow.children = [self.plot]
        #self.bottomrow.children = [self.hist_plot, self.selectr]
        #self.mainrow.children = [self.selectr]
        #self.bottomrow.children = [self.plot]

    def input_change(self, obj, attrname, old, new):
        self.make_source()
        self.make_better_plots()
        self.set_children()
        curdoc().add(self)

    def setup_events(self):
        super(ShoeApp, self).setup_events()
        if self.source:
            self.source.on_change('selected', self, 'selection_change')


    def selection_change(self, obj, attrname, old, new):
        #self.make_brand_plot
        #self.set_children()
        #curdoc().add(self)
        import pdb;pdb.set_trace()
        bdf = self.brand_df
        min_idx, max_idx = shoes_func.min_max_range(ranges, bdf['price'])
        self.configure_brand_source(min_idx, max_idx)
        self.make_brand_source()
        self.make_brand_plot(min_idx, max_idx)
        self.set_children()
        curdoc().add(self)


    @property
    def df(self):
        return _shoedf

    @property
    def brand_df(self):

        pandas_df = self.df
        selected = self.source.selected
        if selected['1d']['indices']:
            idxs = selected['1d']['indices']
            sel_brand = pandas_df.iloc[idxs[0], :]['brand']
            #pandas_df = pandas_df.iloc[idxs, :]
            #return _shoedf[_shoedf['brand'] =='manolo blahnik']
            return _shoedf[_shoedf['brand'] == sel_brand]
        else:
            return pandas_df.iloc[0:0, :]

        #return _shoedf[_shoedf['brand'] =='manolo blahnik']



# The following code adds a "/bokeh/shoes/" url to the bokeh-server. This URL
# will render this ShoeApp. If you don't want serve this applet from a Bokeh
# server (for instance if you are embedding in a separate Flask application),
# then just remove this block of code.
@bokeh_app.route("/bokeh/shoes/")
@object_page("shoes")
def make_shoes():
    app = ShoeApp.create()
    return app
