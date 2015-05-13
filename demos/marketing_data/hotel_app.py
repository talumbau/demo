"""
This file demonstrates a bokeh applet, which can either be viewed
directly on a bokeh-server, or embedded into a flask application.
See the README.md file in this directory for instructions on running.
"""

import logging

logging.basicConfig(level=logging.DEBUG)

from os import listdir
from os.path import dirname, join, splitext

import numpy as np
import pandas as pd
from numpy import pi

from bokeh.models import (ColumnDataSource, Plot,
    GMapPlot, Range1d, LinearAxis,
    PanTool, WheelZoomTool, BoxSelectTool, HoverTool,
    BoxSelectionOverlay, GMapOptions, FactorRange, TapTool,
    NumeralTickFormatter, PrintfTickFormatter,
    CategoricalTickFormatter, CategoricalAxis)

from bokeh.models.glyphs import Circle, Text
from bokeh.plotting import figure, curdoc
from bokeh.properties import String, Instance
from bokeh.server.app import bokeh_app
from bokeh.server.utils.plugins import object_page
from bokeh.models.widgets import HBox, VBox, VBoxForm, PreText, Select



def get_hotel_data():
    import hotel_read
    #return hotel.names, hotel.lats, hotel.longs, hotel.city
    dta, revs = hotel_read.read_data(num_lines=2000)
    dta = pd.DataFrame({'names':dta['name'],
                        'lat':dta['lat'], 'lon':dta['lon'],
                        'city':dta['city'],
                        'ratings':dta['ave_review'],
                        'fill':['yellow'] * len(dta['city']),
                        'fill2':['purple'] * len(dta['city']),
                        'state':dta['state'],
                        'num_reviews':dta['num_reviews']})

    dta = dta.dropna(axis=0)

    #dtaustin = dta[dta['city'] == 'Austin']
    return dta 

hdata = get_hotel_data()

def return_hotel_data():
    return hdata

def get_data():
    n = ['AAA', 'BBB', 'CCC']
    lat=[30.2861, 30.2855, 30.2869]
    lon=[-97.7394, -97.7390, -97.7405]
    city = ["Austin", "Austin", "Austin"]
    ratings=[3.5, 4.5, 2.5]
    num_reviews=[10, 11, 12]
    fill=["yellow"] * 3
    fill2=["green"] * 3
    return pd.DataFrame({'names':n, 'lat':lat, 'lon':lon,
                         'ratings':ratings,
                         'fill':fill,
                         'fill2':fill2,
                         'city':city,
                         'num_reviews':num_reviews})


class HotelApp(VBox):
    extra_generated_classes = [["HotelApp", "HotelApp", "VBox"]]
    jsmodel = "VBox"

    # text statistics
    #pretext = Instance(PreText)

    # input
    selectr = Instance(Select)

    # plots
    plot = Instance(GMapPlot)
    bar_plot = Instance(Plot)

    # data source
    source = Instance(ColumnDataSource)

    # layout boxes
    mainrow = Instance(HBox)
    #histrow = Instance(HBox)
    statsbox = Instance(VBox)

    # inputs
    #ticker1_select = Instance(Select)
    #ticker2_select = Instance(Select)
    #input_box = Instance(VBoxForm)

    def make_inputs(self):
        self.selectr = Select(
            name='states',
            value='Texas',
            options=['Texas', 'Illinois', 'California', 'New York', 'Ohio']
        )

    def __init__(self, *args, **kwargs):
        super(HotelApp, self).__init__(*args, **kwargs)
        self._dfs = {}
        #df, revs = get_hotel_data()
        #self._df = df
        #self._revs = revs

    @classmethod
    def create(cls):
        """
        This function is called once, and is responsible for
        creating all objects (plots, datasources, etc)
        """
        # create layout widgets
        obj = cls()
        obj.mainrow = HBox()
        obj.statsbox = VBox()

        obj.make_inputs()

        # outputs
        #obj.pretext = PreText(text="", width=500)
        obj.make_source()
        obj.make_plots()

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

    def make_plots(self):

        x_range = Range1d()
        y_range = Range1d()
        map_options = GMapOptions(lat=39.8282, lng=-98.5795, zoom=4)
        #map_options = GMapOptions(lat=30.2861, lng=-97.7394, zoom=15)
        plot = GMapPlot(
            x_range=x_range, y_range=y_range,
            map_options=map_options,
            title = "Austin",
            plot_width=800,
            plot_height=600
        )
        plot.map_options.map_type="hybrid"
        circle2 = Circle(x="lon", y="lat", size=10, fill_color="fill2", line_color="black")
        circle = Circle(x="lon", y="lat", size=10, fill_color="fill", line_color="black")
                        #nonselection_fill_color="#FFFF00", nonselection_fill_alpha=1)
        #print "source is ", self.source['lon'], self.source['lat'], self.source['fill']
        plot.add_glyph(self.source, circle, nonselection_glyph=circle2)
        #plot.add_glyph(self.source, circle)
        #rndr = plot.renderers[-1]
        pan = PanTool()
        wheel_zoom = WheelZoomTool()
        box_select = BoxSelectTool()
        #box_select.renderers = [rndr]
        #tooltips = "@name"
        tooltips = "<span class='tooltip-text'>@names</span>\n<br>"
        tooltips += "<span class='tooltip-text'>Reviews: @num_reviews</span>"
        #hover = HoverTool(tooltips="@num_reviews")
        #hover = HoverTool(tooltips="@names")
        hover = HoverTool(tooltips=tooltips)
        tap = TapTool()
        plot.add_tools(pan, wheel_zoom, box_select, hover, tap)
        xaxis = LinearAxis(axis_label="lon", major_tick_in=0, formatter=NumeralTickFormatter(format="0.000"))
        plot.add_layout(xaxis, 'below')
        yaxis = LinearAxis(axis_label="lat", major_tick_in=0, formatter=PrintfTickFormatter(format="%.3f"))
        plot.add_layout(yaxis, 'left')
        #overlay = BoxSelectionOverlay(tool=box_select)
        #plot.add_layout(overlay)

        self.plot = plot
        self.make_bar_plot()

    def make_bar_plot(self):
        # create a new plot
        x_rr = Range1d(start=0.0, end=6.0)
        y_rr = Range1d(start=0.0, end=10.0)
        TOOLS = "box_select,lasso_select"
        bar_plot = figure(tools=TOOLS, width=300, height=400, x_range=x_rr, y_range=y_rr, title=None)

        #x's and y's based on selected_df
        sdf = self.selected_df[['names', 'ratings']]

        xvals = [2.0*i + 0.5 for i in range(0, len(sdf['names']))]
        rightvals = [2.0*i + 1.5 for i in range(0, len(sdf['names']))]
        ratings = [r for r in sdf['ratings']]
        bottoms = [0]*len(ratings)
        y_text = [y + 1.0 for y in ratings]
        all_names = [n for n in sdf['names']]

        print "all_names ", all_names

        #bar_plot.circle(xvals, ratings, size=12)
        bar_plot.quad(xvals, rightvals, ratings, bottoms)

        #glyph = Text(x=xvals, y=y_text, text=sdf['names'], angle=pi/4,
                    #text_align="left", text_baseline="middle")

        glyphs = [Text(x=x, y=y, text=[n], angle=pi/4, text_align="left", text_baseline="middle") 
                  for x, y, n in zip(xvals, y_text, all_names)]
                   
        for g in glyphs:
            bar_plot.add_glyph(g)

        bar_plot.xaxis.major_tick_line_color = "firebrick"
        bar_plot.xaxis.major_tick_line_width = 3
        bar_plot.xaxis.minor_tick_line_color = "orange"

        bar_plot.yaxis.minor_tick_line_color = None

        bar_plot.axis.major_tick_out = 10
        bar_plot.axis.minor_tick_in = -3
        bar_plot.axis.minor_tick_out = 8

        bar_plot.xgrid.grid_line_color = None
        bar_plot.ygrid.grid_line_color = None
        self.bar_plot = bar_plot

    @property
    def selected_df(self):
        print "in selected df"
        pandas_df = self.df
        print "pandas df.columns ", pandas_df.columns
        selected = self.source.selected
        if selected:
            pandas_df = pandas_df.iloc[selected, :]
        return pandas_df

    def set_children(self):
        self.children = [self.mainrow]
        self.mainrow.children = [self.plot, self.statsbox]
        self.statsbox.children = [self.selectr, self.bar_plot]

    def input_change(self, obj, attrname, old, new):
        if obj == self.selectr:
            self.select_val = new

        self.make_source()
        self.make_plots()
        self.set_children()
        curdoc().add(self)


    def setup_events(self):
        super(HotelApp, self).setup_events()
        if self.source:
            self.source.on_change('selected', self, 'selection_change')
        if self.selectr:
            self.selectr.on_change('value', self, 'input_change')

    def selection_change(self, obj, attrname, old, new):
        self.make_stats()
        self.hist_plots()
        self.set_children()
        curdoc().add(self)

    @property
    def df(self):
        #return get_hotel_data()
        thedf = return_hotel_data()
        thedf2 = get_data()
        import pdb;pdb.set_trace()
        return thedf

    def selection_change(self, obj, attrname, old, new):
        self.make_bar_plot()
        self.set_children()
        curdoc().add(self)


# The following code adds a "/bokeh/hotel/" url to the bokeh-server. This URL
# will render this HotelApp. If you don't want serve this applet from a Bokeh
# server (for instance if you are embedding in a separate Flask application),
# then just remove this block of code.
@bokeh_app.route("/bokeh/hotel/")
@object_page("hotel")
def make_hotel():
    app = HotelApp.create()
    return app
