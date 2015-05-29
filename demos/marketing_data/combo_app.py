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
import shoes_func
from read_counties import get_some_counties, color_counties

from bokeh.models import (ColumnDataSource, Plot,
    GMapPlot, Range1d, LinearAxis, Patch, Patches,
    PanTool, WheelZoomTool, BoxSelectTool, HoverTool,
    BoxSelectionOverlay, GMapOptions, FactorRange, TapTool,
    NumeralTickFormatter, PrintfTickFormatter, Callback,
    CategoricalTickFormatter, CategoricalAxis, Text, Rect)

from bokeh.palettes import Spectral11

from chart_constants import PLOT_FORMATS
from chart_constants import (FONT_PROPS_SM, BLUE, RED, GREEN,
                              ORANGE, ORANGE_SHADOW)

FONT_PROPS_SMALLER = dict(FONT_PROPS_SM)
FONT_PROPS_SMALLER['text_font_size'] = '8'
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


pop_brands = ["gucci", "salvatore", "rag & bone", "balenciaga",
              "ash", "chloe", "loeffler randall", "rene caovilla",
              "alexander wang", "lanvin", "alexandre birman",
              "kate spade new york", "miu miu", "sophia webster",
              "alberto fermani", "donald j pliner", "vince",
              "giuseppe zanotti", "michael michael kors",
              "ugg australia", "gianvito rossi", "saint laurent",
              "valentino", "tory burch", "prada", "manolo blahnik",
              "christian louboutin", "jimmy choo", "stuart weitzman"]

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
brand_height = [1.0] * len(_shoedf['price'])
brand_width = [1.0] * len(_shoedf['price'])

brand_aves = shoes_func.average_price_per_brand(b2p)
splitters = [100, 250, 300, 425, 600, 750, 900, 1150, 1300, 1500, 1700, 3000, 9999]
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
_shoedf['brand_height'] = brand_height
_shoedf['width'] = width
_shoedf['brand_width'] = brand_width
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
    legend_plot = Instance(Plot)
    # data source
    source = Instance(ColumnDataSource)
    brand_source = Instance(ColumnDataSource)

    # select
    selectr = Instance(Select)
    selectr_filler = Instance(Plot)

    # layout boxes
    bigbox = Instance(VBox)
    totalbox = Instance(HBox)
    brandbox = Instance(VBox)
    selectrbox = Instance(HBox)

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
        obj.bigbox = VBox(width=670)
        obj.totalbox = HBox()
        obj.brandbox = VBox()
        obj.selectrbox = HBox()

        obj.make_source()
        # outputs
        obj.make_better_plots()

        obj.make_inputs()

        # layout
        obj.set_children()
        return obj



    def make_inputs(self):
        x_range = Range1d(0, 30)
        y_range = Range1d(0, 12)
        self.selectr_filler = Plot(
            x_range=x_range, y_range=y_range, title="", 
            plot_width=30, plot_height=12, min_border=0, 
            **PLOT_FORMATS
        )  


        self.selectr = Select(
            name='brands',
            value='Select A Brand',
            options=pop_brands + ['Select A Brand'],
        )


    def make_source(self):
        self.source = ColumnDataSource(data=self.df)
        self.source.callback = Callback(args=dict(), code="""

            var inds = cb_obj.get('selected')['1d'].indices;
            var theidx = inds[0];
            var d1 = cb_obj.get("data");
            var brand = d1["brand"][theidx];

            console.log("yep");
            console.log(theidx);
            $.get( "shoes", {id: brand}, function( response ) {

                console.log("logging rep");
                console.log(response);
                console.log("done logging rep");
                $( "#child" ).html( response );
            }, "html");
            console.log("done");

        """)



        self.make_brand_source()

    def make_brand_source(self):
        self.brand_source = ColumnDataSource(data=self.brand_df)


    def configure_brand_source(self, min_idx=0, max_idx=MAX_IDX):
        bdf = self.brand_df
        #min_idx, max_idx = shoes_func.min_max_range(ranges, bdf['price'])
        min_idx, max_idx = shoes_func.min_max_range(orig_order, bdf['price'])
        counts = [0] * (max_idx - min_idx + 1)
        for i in bdf.index:
            ans = bdf.ix[i]
            #idx = int(ans['price'] + 100)//100 + 1
            idx = int(ans['price']//100)
            print "idx is ", idx
            print "price is ", ans['price']
            #Categorical stuff
            #xcat.append(ranges[idx-2])
            #_shoedf.loc[i, 'brand_y'] = (counts[idx - min_idx] - 0.5*counts[idx - min_idx])
            _shoedf.loc[i, 'brand_y'] = (counts[idx - min_idx]) + 0.5
            counts[idx - min_idx] = counts[idx - min_idx] + 1
            #quad stuff
            #xvals.append(idx - 0.25)
            #rightvals.append(idx + 0.25)
            #bottoms.append(counts[idx]/2)
            #tops.append(counts[idx] + 0.5)
            #fills.append(brand_to_color[ans['brand']])
        return None



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
        p = figure(tools=TOOLS, width=580, height=1000, y_range=ranges,
                   x_axis_location="above", toolbar_location=None)
        p.yaxis.major_label_orientation = pi/4
        p.yaxis.axis_label_text_font = 'Avenir'


        #p.quad(left='xvals', right='rightvals', top='tops', bottom='bottoms', color='fills', source=self.dfsource)
        #p.rect(x='xcat', y='yvals', width='width', height='height', color='fills', source=self.source)
        p.rect(x='yvals', y='xcat', width='width', height='height', color='fills', source=self.source)
        p.add_tools(hover, tap)

        self.plot = p
        self.make_brand_plot()
        self.make_legend_plot()

    def make_legend_plot(self, min_idx=0, max_idx=MAX_IDX):
        x_range = Range1d(0, 90)
        y_range = Range1d(0, 295)
        x_range = Range1d(0, 580)
        y_range = Range1d(0, 30)

        text_box = Plot(
            x_range=x_range, y_range=y_range, title="", 
            plot_width=580, plot_height=30, min_border=0, 
            **PLOT_FORMATS
        )

        prices_aves = ["67 ", "185", "271", "367", "500", "685", "827", "989", "1242", "1354", "1611"]

        text_box.add_glyph(
                Text(x=2, y=1, text=['Ave:'],  **FONT_PROPS_SMALLER)
        )
        text_box.add_glyph(
            Text(x=24, y=1, text=['$' + prices_aves[0]],  **FONT_PROPS_SMALLER)
        )
        text_box.add_glyph(
            Rect(x=33, y=22, width=23, height=10, 
            fill_color=Spectral11[0], line_color=None)
        )

        for i in range(1,11):
            text_box.add_glyph(
                Text(x=(21 + 52*i), y=1, text=['$' + prices_aves[i]],  **FONT_PROPS_SMALLER)
            )
            text_box.add_glyph(
                Rect(x=33 + 52*i, y=22, width=23, height=10, 
                fill_color=Spectral11[i], line_color=None)
            )

        self.legend_plot = text_box


    def make_brand_plot(self, min_idx=0, max_idx=MAX_IDX):

        TOOLS = "box_select,lasso_select"
        tooltips = "<span class='tooltip-text'>Name: @name</span>\n<br>"
        tooltips += "<span class='tooltip-text'>Brand: @brand</span>\n<br>"
        tooltips += "<span class='tooltip-text'>Price: @price</span>\n<br>"
        hover = HoverTool(tooltips=tooltips)

        bdf = self.brand_df
        if len(bdf) > 0:
            title = "Brand: " + self.brand_df['brand'].values[0]
        else:
            title = ""
        brand_ranges = orig_order[min_idx:max_idx+1]
        p = figure(tools=TOOLS, width=420, height=400, x_range=brand_ranges, title=title, toolbar_location=None)
        p.xaxis.major_label_orientation = pi/4

        p.title_text_font='Avenir'
        p.title_text_font_size='14pt'
        #p.quad(left='xvals', right='rightvals', top='tops', bottom='bottoms', color='fills', source=self.dfsource)
        p.rect(x='xcat', y='brand_y', line_color='black', width='width', height='brand_height', color='fills', source=self.brand_source)
        p.add_tools(hover)

        self.brand_plot = p


    def set_children(self):
        self.children = [self.totalbox]
        self.totalbox.children = [self.bigbox, self.brandbox]
        self.bigbox.children = [self.legend_plot, self.plot]
        self.brandbox.children = [self.selectrbox, self.brand_plot]
        self.selectrbox.children = [self.selectr_filler, self.selectr]
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

        if self.selectr:
            self.selectr.on_change('value', self, 'brand_change')

    def selection_change(self, obj, attrname, old, new):
        #self.make_brand_plot
        #self.set_children()
        #curdoc().add(self)
        bdf = self.brand_df
        min_idx, max_idx = shoes_func.min_max_range(ranges, bdf['price'])
        self.configure_brand_source(min_idx, max_idx)
        self.make_brand_source()
        self.make_brand_plot(min_idx, max_idx)
        self.set_children()
        curdoc().add(self)

    def brand_change(self, obj, attrname, old, new):
        bdf = self.brand_df
        if self.selectr.value is None or self.selectr.value == 'Select A Brand':
            return
        self.update_selected_on_source(self.selectr.value)
        self.set_children()
        curdoc().add(self)

    def update_selected_on_source(self, brand):
        # {'2d': {'indices': []}, '1d': {'indices': []}, '0d': {'indices': [], 'flag': False}}
        brand_df = _shoedf[ _shoedf['brand'] == brand ]

        new_indices = {'2d': {'indices': []}, '1d': {'indices': []}, '0d': {'indices': [], 'flag': False}}
        for _id in brand_df.index:
            new_indices['1d']['indices'].append(_id)

        self.source.selected = new_indices


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


class HotelApp(VBox):
    extra_generated_classes = [["HotelApp", "HotelApp", "VBox"]]
    jsmodel = "VBox"

    # input
    selectr = Instance(Select)
    #check_group = Instance(RadioGroup)
    check_group = Instance(CheckboxGroup)

    # plots
    plot = Instance(GMapPlot)
    filler = Instance(Plot)
    filler2 = Instance(Plot)
    bar_plot = Instance(Plot)
    legend_plot = Instance(Plot)
    legend_filler = Instance(Plot)

    # data source
    source = Instance(ColumnDataSource)
    county_source = Instance(ColumnDataSource)

    # layout boxes
    checkbox = Instance(VBox)
    mainrow = Instance(HBox)
    statsbox = Instance(VBox)
    mapbox = Instance(VBox)
    legendbox = Instance(HBox)
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
            options=[s[1] for s in states] + ['Choose A State'],
        )
        labels = ["County Averages", "Hotels"]
        self.check_group = CheckboxGroup(labels=labels, active=[0,1], inline=True)
        ##Filler plot
        x_range = Range1d(0, 300)
        y_range = Range1d(0, 12)
        self.filler = Plot(
            x_range=x_range, y_range=y_range, title="", 
            plot_width=300, plot_height=12, min_border=0, 
            **PLOT_FORMATS
        )  
        x_range = Range1d(0, 300)
        y_range = Range1d(0, 18)
        self.filler2 = Plot(
            x_range=x_range, y_range=y_range, title="", 
            plot_width=300, plot_height=14, min_border=0, 
            **PLOT_FORMATS
        )  




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
        obj.checkbox = VBox(height=50)
        obj.mapbox = VBox()
        #obj.bottomrow = HBox()
        obj.statsbox = VBox( width=500)
        obj.totalbox = VBox()
        obj.legendbox = HBox()

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

        new_data = {}
        for col in df:
            new_data[col] = df[col]

        self.source.data = new_data

    def make_county_source(self):
        self.county_source = ColumnDataSource(data=self.countydf)

    def update_county_source(self):
        if self.selectr.value is None or self.selectr.value == 'Choose A State':
            df = county_data
        else:
            df = county_data[county_data['state'] == self.selectr.value]

        new_data = {}
        for col in df:
            new_data[col] = df[col]

        self.county_source.data = new_data
        #for col in df:
        #    self.county_source.data[col] = df[col]


    def make_plots(self):
        self.create_map_plot()
        self.create_legend()
        self.populate_glyphs()
        self.make_bar_plot()

    def create_legend(self):

        x_range = Range1d(0, 185)
        y_range = Range1d(0, 130)

        text_box = Plot(
            x_range=x_range, y_range=y_range, title="", 
            plot_width=185, plot_height=130, min_border=0, 
            **PLOT_FORMATS
        )  

        FONT_PROPS_SM['text_font_size'] = '11pt'
        text_box.add_glyph(
            Text(x=35, y=9, text=['Low Average Rating'],  **FONT_PROPS_SM)
        )
        text_box.add_glyph(
            Rect(x=18, y=18, width=25, height=25, 
                fill_color='#ef4e4d', line_color=None)
        )
        text_box.add_glyph(
            Text(x=35, y=49, text=['Medium Average Rating'],  **FONT_PROPS_SM)
        )
        text_box.add_glyph(
            Rect(x=18, y=58, width=25, height=25, 
                fill_color='#14a1af', line_color=None)
        )

        text_box.add_glyph(
            Text(x=35, y=89, text=['High Average Rating'],  **FONT_PROPS_SM)
        )
        text_box.add_glyph(
            Rect(x=18, y=98, width=25, height=25, 
                fill_color='#743184', line_color=None)
        )

        self.legend_plot = text_box

        ##Filler plot
        x_range = Range1d(0, 40)
        y_range = Range1d(0, 100)
        self.legend_filler = Plot(
            x_range=x_range, y_range=y_range, title="", 
            plot_width=40, plot_height=100, min_border=0, 
            **PLOT_FORMATS
        )  
 


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
            plot_width=680,
            plot_height=600,
            title=" "
        )
        plot.map_options.map_type="hybrid"
        xaxis = LinearAxis(axis_label="lon", major_tick_in=0, formatter=NumeralTickFormatter(format="0.000"))
        plot.add_layout(xaxis, 'below')
        yaxis = LinearAxis(axis_label="lat", major_tick_in=0, formatter=PrintfTickFormatter(format="%.3f"))
        plot.add_layout(yaxis, 'left')

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
            circle2 = Circle(x="lon", y="lat", size=10, fill_color="fill2", fill_alpha=1.0, line_color="black")
            circle = Circle(x="lon", y="lat", size=10, fill_color="fill", fill_alpha=1.0, line_color="black")
            #print "source is ", self.source['lon'], self.source['lat'], self.source['f1ll']
            self.plot.add_glyph(self.source, circle2, nonselection_glyph=circle, name='hotels')
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
        y_rr = Range1d(start=0.0, end=5.0)
        TOOLS = "box_select,lasso_select"

        #x's and y's based on selected_df
        sdf = self.selected_df[['names', 'ratings']]

        xvals = [1.0*i + 0.5 for i in range(0, len(sdf['names']))]
        rightvals = [1.0*i + 0.85 for i in range(0, len(sdf['names']))]
        ratings = [r for r in sdf['ratings']]
        centers = [0.5*r for r in ratings]
        bottoms = [0]*len(ratings)
        y_text = [y + 1.0 for y in ratings]
        width = [1.0] * len(ratings)
        all_names = []
        for n in sdf['names']:
            short_name = n[:20]
            idx = short_name.rfind(" ")
            all_names.append(short_name[:idx])

        while len(all_names) > 0 and len(all_names) < 5:
            all_names.append("   ")

        bar_plot = figure(tools=TOOLS, width=400, height=350, x_range=all_names, y_range=y_rr, title="Average Rating")
        bar_plot.title_text_color = "black"
        bar_plot.title_text_font_size='15pt'
        bar_plot.title_text_font='Avenir'
        bar_plot.title_text_align = "right"
        print "all_names ", all_names

        bar_colors = []
        for r in ratings:
            if r >= 4.0:
                bar_colors.append("#743184")
            elif r >= 3.0:
                bar_colors.append("#14a1af")
            else:
                bar_colors.append("#ef4e4d")

        bar_plot.xaxis.major_label_orientation = pi/2.3
        bar_plot.rect(x=all_names, y=centers, width=width, height=ratings, color=bar_colors, line_color="black")

        #glyph = Text(x=xvals, y=y_text, text=sdf['names'], angle=pi/4,
                    #text_align="left", text_baseline="middle")

        #glyphs = [Text(x=x, y=y, text=[n], angle=pi/4, text_align="left", text_baseline="middle") 
                  #for x, y, n in zip(xvals, y_text, all_names)]
                   

        bar_plot.xaxis.major_tick_line_color = None
        bar_plot.xaxis.minor_tick_line_color = None

        bar_plot.yaxis.minor_tick_line_color = None


        bar_plot.xgrid.grid_line_color = None
        bar_plot.ygrid.grid_line_color = None
        self.bar_plot = bar_plot


    def set_children(self):
        self.children = [self.totalbox]
        self.totalbox.children = [self.mainrow]
        self.mainrow.children = [self.statsbox, self.mapbox]
        self.mapbox.children = [self.plot]
        #self.checkbox.children = [self.filler, self.check_group, self.filler2]
        self.statsbox.children = [self.bar_plot, self.legendbox]
        self.legendbox.children = [self.legend_filler, self.legend_plot]
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
        #import pdb;pdb.set_trace()
        print "source len: ", len(self.source.data['state'])
        print "county len: ", len(self.county_source.data['names'])
        self.update_source()
        self.update_county_source()
        print "source len: ", len(self.source.data['state'])
        print "county len: ", len(self.county_source.data['names'])
        if self.selectr.value is None or self.selectr.value == 'Choose A State':
            pass
        else:
            self.plot.title = self.selectr.value




