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

from bokeh.models import ColumnDataSource, Plot, HoverTool
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

def get_shoe_data():
    b2p = shoes_func.get_brands_to_prices()
    b2p_small = {}
    for count, k in zip(range(0,30), b2p):
        b2p_small[k] = b2p[k]
    return b2p_small

b2p = get_shoe_data()
#df = pd.DataFrame(b2p)
brands = [k for k in zip(range(0,20), b2p.keys())]

_shoedf = shoes_func.get_all_shoes()
idx = (_shoedf['price'] + 100)//100
idx = [int(x) + 1 for x in idx]
counts = [0] * len(ranges)
colors = bokeh.palettes.PRGn11
xvals = []
yvals = []
xcat = []
rightvals = []
tops = []
bottoms = []
fills = []
height = [0.5] * len(_shoedf['price'])
width = [0.5] * len(_shoedf['price'])

for i in _shoedf.index:
    ans = _shoedf.ix[i]
    idx = int(ans['price'] + 100)//100 + 1
    print "idx is ", idx
    print "price is ", ans['price']
    #Categorical stuff
    xcat.append(ranges[idx-2])
    yvals.append(counts[idx] - 0.5*counts[idx])

    #quad stuff
    xvals.append(idx - 0.25)
    rightvals.append(idx + 0.25)
    bottoms.append(counts[idx]/2)
    tops.append(counts[idx] + 0.5)
    counts[idx] = counts[idx] + 1
    fills.append(colors[(random.randint(0, 10000) % 11)])

_shoedf['xvals'] = xvals
_shoedf['xcat'] = xcat
_shoedf['rightvals'] = rightvals
_shoedf['bottoms'] = bottoms
_shoedf['tops'] = tops
_shoedf['fills'] = fills
_shoedf['yvals'] = yvals
_shoedf['height'] = height
_shoedf['width'] = width


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
    hist_plot = Instance(Plot)
    # data source
    source = Instance(ColumnDataSource)
    dfsource = Instance(ColumnDataSource)

    # input
    selectr = Instance(Select)

    # layout boxes
    mainrow = Instance(HBox)
    bottomrow = Instance(HBox)
    totalbox = Instance(VBox)

    def __init__(self, *args, **kwargs):
        super(ShoeApp, self).__init__(*args, **kwargs)
        self._dfs = {}

    @classmethod
    def create(cls):
        """
        This function is called once, and is responsible for
        creating all objects (plots, datasources, etc)
        """
        # create layout widgets
        obj = cls()
        obj.mainrow = HBox()
        obj.bottomrow = HBox()
        obj.totalbox = VBox()

        obj.make_source()
        # outputs
        obj.make_inputs()
        #obj.make_plots()
        obj.make_better_plots()

        # layout
        obj.set_children()
        return obj

    @property
    def selected_df(self):
        pandas_df = self.df
        selected = self.source.selected
        if selected:
            pandas_df = pandas_df.iloc[selected, :]
        return pandas_df

    def make_source(self):
        self.source = ColumnDataSource(data=self.df)
        self.dfsource = ColumnDataSource(data=self.shoedf)

    def make_inputs(self):

        self.selectr = Select(
            name='brands',
            options=b2p.keys() + ['Choose a Brand']
        )

    def make_plots(self):

        bins = np.arange(0.0, 4000, 100)
        bins2 = np.concatenate((bins, np.array([8000.0])))
        b2p_stacked = { k: make_row(np.digitize(v, bins), len(bins2)) for k,v in b2p.iteritems()}

        bar = Bar(b2p_stacked, ranges, title="Price Distribution", stacked=True, width=1100, height=700,
                  legend="top_right")

        self.plot = bar
        self.make_hist_plot()

    def make_better_plots(self):
        
        """sdf = self.shoedf
        idx = (sdf['price'] + 100)//100
        idx = [int(x) + 1 for x in idx]
        counts = [0] * len(ranges)
        colors = ["blue", "orange", "green", "yellow", "purple"]
        xvals = []
        rightvals = []
        bottoms = []
        fills = []
        height = [1] * len(sdf['price'])

        for i in sdf.index:
            ans = sdf.ix[i]
            idx = int(ans['price'] + 100)//100 + 1
            print "idx is ", idx
            print "price is ", ans['price']
            xvals.append(idx - 0.25)
            rightvals.append(idx + 0.25)
            bottoms.append(counts[idx])
            counts[idx] = counts[idx] + 1
            fills.append(colors[idx % 5])"""

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
        p = figure(tools=TOOLS, width=1100, height=700, x_range=ranges, title="Price Distribution")
        p.xaxis.major_label_orientation = pi/4

        #p.quad(left='xvals', right='rightvals', top='tops', bottom='bottoms', color='fills', source=self.dfsource)
        p.rect(x='xcat', y='yvals', width='width', height='height', color='fills', source=self.dfsource)
        p.add_tools(hover)

        self.plot = p
        self.make_hist_plot()

    def make_hist_plot(self):
        """global_hist, global_bins = np.histogram(self.df[ticker + "_returns"], bins=50)
        hist, bins = np.histogram(self.selected_df[ticker + "_returns"], bins=50)
        width = 0.7 * (bins[1] - bins[0])
        center = (bins[:-1] + bins[1:]) / 2
        start = global_bins.min()
        end = global_bins.max()
        top = hist.max()"""

        """p = figure(
            title="Brand histogram",
            plot_width=800, plot_height=400,
            tools="",
            title_text_font_size="10pt",
            x_range=[0, 1000],
            y_range=[0, 2],
        )"""

        
        if self.selectr.value is None or self.selectr.value == 'Choose A Brand':
            p = figure(
                title="Brand histogram",
                plot_width=800, plot_height=400,
                tools="",
                title_text_font_size="10pt",
                x_range=[0, 1000],
                y_range=[0, 2])
            self.hist_plot = p

        else:
            df = pd.DataFrame({'prices':b2p[self.selectr.value]})
            print "prices are ", b2p[self.selectr.value]
            self.hist_plot = Histogram(df, bins=200, width=800, height=400, legend=True)


    def set_children(self):
        self.children = [self.totalbox]
        #self.totalbox.children = [self.plot]
        self.totalbox.children = [self.mainrow, self.bottomrow]
        self.mainrow.children = [self.plot]
        self.bottomrow.children = [self.hist_plot, self.selectr]
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
        if self.selectr:
            self.selectr.on_change('value', self, 'input_change')


    def selection_change(self, obj, attrname, old, new):
        self.set_children()
        curdoc().add(self)

    @property
    def df(self):
        return get_shoe_data()

    @property
    def shoedf(self):
        return _shoedf


# The following code adds a "/bokeh/shoes/" url to the bokeh-server. This URL
# will render this ShoeApp. If you don't want serve this applet from a Bokeh
# server (for instance if you are embedding in a separate Flask application),
# then just remove this block of code.
@bokeh_app.route("/bokeh/shoes/")
@object_page("shoes")
def make_shoes():
    app = ShoeApp.create()
    return app
