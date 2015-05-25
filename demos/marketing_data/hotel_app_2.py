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
from read_counties import get_some_counties, color_counties

from bokeh.models import (ColumnDataSource, Plot,
    GMapPlot, Range1d, LinearAxis, Patch, Patches,
    PanTool, WheelZoomTool, BoxSelectTool, HoverTool,
    BoxSelectionOverlay, GMapOptions, FactorRange, TapTool,
    NumeralTickFormatter, PrintfTickFormatter, Callback,
    CategoricalTickFormatter, CategoricalAxis)

from bokeh.models.glyphs import Circle, Text
from bokeh.plotting import figure, curdoc
from bokeh.properties import String, Instance
from bokeh.server.app import bokeh_app
from bokeh.server.utils.plugins import object_page
from bokeh.models.widgets import (HBox, VBox, VBoxForm, PreText, Paragraph, Select,
                                  RadioGroup, CheckboxGroup)

from bokeh.models.renderers import GlyphRenderer
import hotel_read


hdata, hrevs = hotel_read.get_hotel_data()

county_data = get_some_counties()
zeroed_counties = [0] * len(county_data['names'])
full_counties = [1] * len(county_data['names'])
zeroed_hotels = [0] * len(hdata['state'])
full_hotels = [1] * len(hdata['state'])
#hdata['alpha'] = full_hotels

color_counties(hdata, county_data)

county_data = pd.DataFrame(county_data)

def return_hotel_data():
    return hdata

def return_hotel_reviews():
    return hrevs


colors = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]


class HotelApp(VBox):
    extra_generated_classes = [["HotelApp", "HotelApp", "VBox"]]
    jsmodel = "VBox"

    # input
    selectr = Instance(Select)
    #check_group = Instance(RadioGroup)
    check_group = Instance(CheckboxGroup)

    # plots
    plot = Instance(GMapPlot)
    bar_plot = Instance(Plot)

    # data source
    source = Instance(ColumnDataSource)
    county_source = Instance(ColumnDataSource)

    # layout boxes
    mainrow = Instance(HBox)
    #bottomrow = Instance(HBox)
    statsbox = Instance(VBox)
    totalbox = Instance(VBox)

    # inputs
    #ticker1_select = Instance(Select)
    #ticker2_select = Instance(Select)
    #input_box = Instance(VBoxForm)

    def make_inputs(self):
        with open("states.csv") as f:
            states = [line.strip().split(',') for line in f.readlines()]

        self.selectr = Select(
            name='states',
            value='Choose A State',
            options=[s[1] for s in states] + ['Choose A State']
        )
        labels = ["County Averages", "Hotels"]
        self.check_group = CheckboxGroup(labels=labels, active=[0,1])

    def make_outputs(self):
        pass
        #self.pretext = Paragraph(text="", width=800)

    def __init__(self, *args, **kwargs):
        super(HotelApp, self).__init__(*args, **kwargs)
        self._show_counties = True
        self._show_hotels = True

    @classmethod
    def create(cls):
        """
        This function is called once, and is responsible for
        creating all objects (plots, datasources, etc)
        """
        # create layout widgets
        obj = cls()
        obj.mainrow = HBox()
        #obj.bottomrow = HBox()
        obj.statsbox = VBox()
        obj.totalbox = VBox()

        labels = ["County Average Ratings", "Hotel Locations"]
        obj.make_inputs()
        obj.make_outputs()

        # outputs
        #obj.pretext = Paragraph(text="", width=500)
        obj.make_source()
        obj.make_county_source()
        lat=39.8282
        lng=-98.5795
        zoom=6
        xr = Range1d()
        yr = Range1d()
        #obj.make_plots(lat, lng, zoom, xr, yr)
        obj.make_plots()

        # layout
        obj.set_children()
        return obj

    @property
    def selected_df(self):
        pandas_df = self.df
        selected = self.source.selected
        print "seeing if selected!"
        if selected:
            idxs = selected['1d']['indices']
            pandas_df = pandas_df.iloc[idxs, :]
        else:
            pandas_df = pandas_df.iloc[0:0, :]
        return pandas_df


    def make_source(self):
        self.source = ColumnDataSource(data=self.df)
        self.source.callback = Callback(args=dict(), code="""

            var inds = cb_obj.get('selected')['1d'].indices;
            var theidx = inds[0];

            console.log("yep");
            console.log(theidx);
            $.get( "reviews", {id: theidx}, function( response ) {
                $( "#section2" ).html( response );
            }, "html");
            console.log("done");
        """)


    def update_source(self):
        if self.selectr.value is None or self.selectr.value == 'Choose A State':
            df = hdata
        else:
            df = hdata[hdata['state'] == self.selectr.value]

        for col in df:
            self.source.data[col] = df[col]

    def make_county_source(self):
        self.county_source = ColumnDataSource(data=self.countydf)

    def update_county_source(self):
        if self.selectr.value is None or self.selectr.value == 'Choose A State':
            df = county_data
        else:
            df = county_data[county_data['state'] == self.selectr.value]

        for col in df:
            self.county_source.data[col] = df[col]



    """def init_check_group(self):

        print "initing radio group"
        self.check_group.on_click(self.check_group_handler)

    def check_group_handler(self, active):
        print "radio group handler %s" % active"""

    def make_plots(self):
        self.create_map_plot()
        self.populate_glyphs()
        self.make_bar_plot()

    #def make_plots(self):
    def create_map_plot(self):
        lat=39.8282
        lng=-98.5795
        zoom=6
        xr = Range1d()
        yr = Range1d()
        x_range = xr
        y_range = yr
        #map_options = GMapOptions(lat=39.8282, lng=-98.5795, zoom=6)
        map_options = GMapOptions(lat=lat, lng=lng, zoom=zoom)
        #map_options = GMapOptions(lat=30.2861, lng=-97.7394, zoom=15)
        plot = GMapPlot(
            x_range=x_range, y_range=y_range,
            map_options=map_options,
            title = "Hotel Review Explorer",
            plot_width=680,
            plot_height=600
        )
        plot.map_options.map_type="hybrid"
        xaxis = LinearAxis(axis_label="lon", major_tick_in=0, formatter=NumeralTickFormatter(format="0.000"))
        plot.add_layout(xaxis, 'below')
        yaxis = LinearAxis(axis_label="lat", major_tick_in=0, formatter=PrintfTickFormatter(format="%.3f"))
        plot.add_layout(yaxis, 'left')

        #pan = PanTool()
        #wheel_zoom = WheelZoomTool()
        #box_select = BoxSelectTool()
        #box_select.renderers = [rndr]
        #tooltips = "@name"
        #tooltips = "<span class='tooltip-text'>@names</span>\n<br>"
        #tooltips += "<span class='tooltip-text'>Reviews: @num_reviews</span>"
        #hover = HoverTool(tooltips="@num_reviews")
        #hover = HoverTool(tooltips="@names")
        #hover = HoverTool(tooltips=tooltips)
        #tap = TapTool()
        #plot.add_tools(pan, wheel_zoom, box_select, hover, tap)
        #plot.add_tools(hover, tap)
        #overlay = BoxSelectionOverlay(tool=box_select)
        #plot.add_layout(overlay)
        #plot.add_glyph(self.source, circle)
        #county_xs, county_ys = get_some_counties()
        #apatch = Patch(x=county_xs, y=county_ys, fill_color=['white']*len(county_xs))
        #plot.add_glyph(apatch)
        self.plot = plot


    def populate_glyphs(self):
        self.plot.renderers=[]
        self.plot.tools=[]
        if self._show_counties:
            print "showing you the counties"
            #datasource = ColumnDataSource(county_data)
            #apatch = Patches(xs=county_xs, ys=county_ys, fill_color='white')
            #apatch = Patches(xs='xs', ys='ys', fill_color='colors', fill_alpha="alpha")
            apatch = Patches(xs='xs', ys='ys', fill_color='thecolors', fill_alpha='alpha')
            self.plot.add_glyph(self.county_source, apatch, name='counties')

        if self._show_hotels:
            print "showing you the hotels"
            circle2 = Circle(x="lon", y="lat", size=10, fill_color="fill2", fill_alpha=1.0, line_alpha=0.0)
            circle = Circle(x="lon", y="lat", size=10, fill_color="fill", fill_alpha=1.0, line_color="black")
            #print "source is ", self.source['lon'], self.source['lat'], self.source['f1ll']
            self.plot.add_glyph(self.source, circle, nonselection_glyph=circle2, name='hotels')
            #county_xs, county_ys = get_some_counties()

        rndr = self.plot.renderers[-1]
        pan = PanTool()
        wheel_zoom = WheelZoomTool()
        box_select = BoxSelectTool()
        box_select.renderers = [rndr]
        tooltips = "@name"
        tooltips = "<span class='tooltip-text'>@names</span>\n<br>"
        tooltips += "<span class='tooltip-text'>Reviews: @num_reviews</span>"
        hover = HoverTool(tooltips=tooltips, names=['hotels'])
        tap = TapTool(names=['hotels'])
        self.plot.add_tools(pan, wheel_zoom, box_select, hover, tap)
        overlay = BoxSelectionOverlay(tool=box_select)
        self.plot.add_layout(overlay)

    def make_bar_plot(self):
        # create a new plot
        x_rr = Range1d(start=0.0, end=6.0)
        y_rr = Range1d(start=0.0, end=10.0)
        TOOLS = "box_select,lasso_select"
        bar_plot = figure(tools=TOOLS, width=400, height=350, x_range=x_rr, y_range=y_rr, title="Average Rating")

        #x's and y's based on selected_df
        sdf = self.selected_df[['names', 'ratings']]

        xvals = [1.0*i + 0.5 for i in range(0, len(sdf['names']))]
        rightvals = [1.0*i + 0.85 for i in range(0, len(sdf['names']))]
        ratings = [r for r in sdf['ratings']]
        bottoms = [0]*len(ratings)
        y_text = [y + 1.0 for y in ratings]
        all_names = [n for n in sdf['names']]

        print "all_names ", all_names

        #bar_plot.circle(xvals, ratings, size=12)
        bar_plot.quad(xvals, rightvals, ratings, bottoms, fill="teal")

        #glyph = Text(x=xvals, y=y_text, text=sdf['names'], angle=pi/4,
                    #text_align="left", text_baseline="middle")

        glyphs = [Text(x=x, y=y, text=[n], angle=pi/4, text_align="left", text_baseline="middle") 
                  for x, y, n in zip(xvals, y_text, all_names)]
                   
        for g in glyphs:
            bar_plot.add_glyph(g)

        bar_plot.xaxis.major_tick_line_color = None
        bar_plot.xaxis.minor_tick_line_color = None
        #bar_plot.xaxis.major_tick_line_width = 3
        #bar_plot.xaxis.minor_tick_line_color = "orange"

        bar_plot.yaxis.minor_tick_line_color = None


        bar_plot.xgrid.grid_line_color = None
        bar_plot.ygrid.grid_line_color = None
        self.bar_plot = bar_plot

    def set_children(self):
        self.children = [self.totalbox]
        self.totalbox.children = [self.mainrow]
        self.mainrow.children = [self.statsbox, self.plot]
        self.statsbox.children = [self.selectr, self.check_group, self.bar_plot]
        #self.bottomrow.children = [self.pretext]


    def setup_events(self):
        super(HotelApp, self).setup_events()
        if self.source:
            self.source.on_change('selected', self, 'selection_change')
        if self.selectr:
            self.selectr.on_change('value', self, 'input_change')
        if self.check_group:
            self.check_group.on_change('active', self, 'check_change')

    @property
    def df(self):
        thedf = return_hotel_data()
        if self.selectr.value is None or self.selectr.value == 'Choose A State':
            return thedf
        else:
            newdf = thedf[thedf['state'] == self.selectr.value]
            return newdf

    @property
    def countydf(self):
        thedf = county_data
        if self.selectr.value is None or self.selectr.value == 'Choose A State':
            return thedf
        else:
            newdf = thedf[thedf['state'] == self.selectr.value]
            return newdf


    def selection_change(self, obj, attrname, old, new):
        #self.make_source()
        self.update_source()
        self.make_bar_plot()
        self.set_children()
        curdoc().add(self)

    def check_change(self, obj, attrname, old, new):
        #Turn on/off the counties/hotel data
        print "what the heck ", obj, attrname, old, new
        if 0 in new:
            self._show_counties = True
        else:
            self._show_counties = False

        if 1 in new:
            self._show_hotels = True
        else:
            self._show_hotels = False

        self.populate_glyphs()
        self.set_children()
        curdoc().add(self)

    def input_change(self, obj, attrname, old, new):
        self.make_source()
        self.make_county_source()
        print "source len: ", len(self.source.data['state'])
        print "county len: ", len(self.county_source.data['names'])
        if self.selectr.value is None or self.selectr.value == 'Choose A State':
            pass
        else:
            self.plot.title = self.selectr.value
        self.populate_glyphs()

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
