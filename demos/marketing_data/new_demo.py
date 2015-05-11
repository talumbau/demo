from __future__ import print_function

import time
import datetime
from math import pi

from requests.exceptions import ConnectionError
import pandas as pd
from bokeh.models import (Plot, ColumnDataSource, DataRange1d, FactorRange,
                           LinearAxis, CategoricalAxis, Grid, Glyph)
from bokeh.models.widgets import (DateRangeSlider, HBox, VBox, Paragraph,
                                  Select, VBoxModelForm)
from bokeh.glyphs import Rect
from bokeh.document import Document
from bokeh.session import Session

import employment_data_reader as emp
from employment_utils import get_country_for_byte, get_jobtype_for_byte

document = Document()
session = Session()
session.use_doc('employment_server')
session.load_document(document)

days_of_week = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
                4: "Friday", 5: "Saturday", 6: "Sunday"}
bounds_start = datetime.date(2012, 11, 1)
bounds_end = datetime.date(2013, 12, 30)
start = datetime.date(2013, 5, 26)
end = datetime.date(2013, 7, 5)
source_country = ColumnDataSource(data=dict())
source_dow = ColumnDataSource(data=dict())
source_jobtype = ColumnDataSource(data=dict())
source_par = Paragraph()
country_choices = ["Dominican Republic___________________",
                   "Colombia_____________________________",
                   "Mexico_______________________________",
                   "Peru_________________________________",
                   "Argentina____________________________"]

countries = ["Brazil",
             "Canada",
             "Italy",
             "Panama",
             "Costa Rica",
             "Saint Martin",
             "Peru",
             "Argentina",
             "Bolivia",
             "Venezuela",
             "Ecuador",
             "El Salvador",
             "China",
             "Chile",
             "Puerto Rico",
             "Dominican Republic",
             "Spain",
             "Dubai",
             "United States",
             "Islands",
             "Romania",
             "Mexico",
             "Uruguay",
             "United Kingdom",
             "Colombia",
             "Paraguay"]

df = None
cur_country = "Dominican Republic"


def weekday_builder():
    dow = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
           "Saturday", "Sunday"]
    xdr = FactorRange(factors=dow)
    ydr = DataRange1d(sources=[source_dow.columns("data_range")])
    plot = Plot(title="Weekday of Job Posting", data_sources=[source_dow],
                x_range=xdr, y_range=ydr, plot_width=760, plot_height=500)
    xaxis = CategoricalAxis(plot=plot, dimension=0, major_label_orientation=pi/4.0)
    yaxis = LinearAxis(plot=plot, dimension=1)
    yaxis.major_tick_in = 0
    ygrid = Grid(plot=plot, dimension=1, axis=yaxis)
    quad = Rect(x="weekday", y="weekday_half",
                height="count", width=0.9,
                fill_color="#D9301A")
    bars = Glyph(data_source=source_dow, xdata_range=xdr,
                 ydata_range=ydr, glyph=quad)
    plot.renderers.append(bars)
    plot.background_fill = '#686975'
    return plot


def jobtype_builder():
    jtypes = ["Half Time", "Full Time", "Hourly", "Temporary"]
    xdr = FactorRange(factors=jtypes)
    ydr = DataRange1d(sources=[source_jobtype.columns("data_range")])
    plot = Plot(title="Job Type", data_sources=[source_jobtype],
                x_range=xdr, y_range=ydr, plot_width=760, plot_height=500)
    xaxis = CategoricalAxis(plot=plot, dimension=0, major_label_orientation=pi/4.0)
    yaxis = LinearAxis(plot=plot, dimension=1)
    yaxis.major_tick_in = 0
    ygrid = Grid(plot=plot, dimension=1, axis=yaxis)
    quad = Rect(x="jobtypes", y="jobtype_half",
                height="count", width=0.9,
                fill_color="#33A6A4")
    bars = Glyph(data_source=source_jobtype, xdata_range=xdr,
                 ydata_range=ydr, glyph=quad)
    plot.renderers.append(bars)
    plot.background_fill = '#686975'
    return plot


def job_loc_plot_builder():
    xdr = FactorRange(factors=countries)
    ydr = DataRange1d(sources=[source_country.columns("data_range")])

    plot = Plot(title="Postings by Job Location (Country)",
                data_sources=[source_country],
                x_range=xdr, y_range=ydr, plot_width=760, plot_height=500)

    xaxis = CategoricalAxis(plot=plot, dimension=0, major_label_orientation=pi/4.0)
    yaxis = LinearAxis(plot=plot, dimension=1)

    yaxis.major_tick_in = 0

    ygrid = Grid(plot=plot, dimension=1, axis=yaxis)

    quad = Rect(x="country", y="count_half",
                height="count", width=0.9,
                fill_color="#483D8B")
    bars = Glyph(data_source=source_country, xdata_range=xdr,
                 ydata_range=ydr, glyph=quad)
    plot.renderers.append(bars)
    plot.background_fill = '#333333'
    return plot


def update_data():
    global df, countries, start, end, cur_country
    dowdf, locdf, typdf, num_records = emp.get_jobs_between_dates_pytables_bytes(start, end,
                                                        cur_country)
    locdf.columns = ['Location', 'Count']
    locdf['Location'] = locdf['Location'].apply(get_country_for_byte)
    df = locdf

    print("start: " + str(start))
    print("end: " + str(end))

    count = df['Count']
    count_half = df['Count'] / 2
    countries = df['Location']
    data_range = df['Count'].copy()

    # Define data range to include zero
    data_range[data_range.idxmin()] = 0

    source_country.data = dict(
        country=countries,
        count_half=count_half,
        count=count,
        data_range=data_range)

    dowdf.columns = ['WeekDay', 'Count']
    dowdf['WeekDay'] = dowdf['WeekDay'].apply(lambda x: days_of_week[x])
    dfwd = dowdf

    count = dfwd['Count']
    weekday_half = dfwd['Count'] / 2
    weekdays = dfwd['WeekDay']
    data_range = dfwd['Count'].copy()

    source_dow.data = dict(
        weekday=weekdays,
        weekday_half=weekday_half,
        count=count,
        data_range=data_range)

    typdf.columns = ['Type', 'Count']
    typdf['Type'] = typdf['Type'].apply(get_jobtype_for_byte)
    dfjt = typdf

    count = dfjt['Count']
    types_half = dfjt['Count'] / 2
    types = dfjt['Type']
    data_range = dfjt['Count'].copy()

    source_jobtype.data = dict(
        jobtypes=types,
        jobtype_half=types_half,
        count=count,
        data_range=data_range)

    full_text = "Number of Records: " + str(num_records)
    full_text += ("\n\n    Approximate size: " + str(0.000336*num_records)
                  + " MB")
    source_par.text = full_text
    session.store_document(document)


def on_country_change(obj, attr, old, new):
    global cur_country
    field_val = new
    cur_country = field_val.strip("_")
    update_data()


def on_date_change(obj, attr, old, new):
    global start, end

    start, end = new
    try:
        # If the datetime is still serialized from Bokeh
        #   it lives in the Backbone model as milliseconds
        start = datetime.date.fromtimestamp(start/1000.)
        end = datetime.date.fromtimestamp(end/1000.)
    except TypeError:
        # Else the datetime has been updated by the widget,
        #   and has to be pulled out of the string.
        start = datetime.datetime.strptime(start[:-5], '%Y-%m-%dT%H:%M:%S')
        end = datetime.datetime.strptime(end[:-5], '%Y-%m-%dT%H:%M:%S')

    update_data()


def layout():

    date_select = DateRangeSlider(
        name="period",
        title="Period:",
        value=(start, end),
        bounds=(bounds_start, bounds_end),
        value_labels='show',
        range=(dict(days=1), None))
    date_select.on_change('value', on_date_change)

    country_select = Select(title="Host Site Country:", value="World",
                            options=country_choices)
    country_select.on_change('value', on_country_change)

    controls = VBoxModelForm(_children=[Paragraph(text="Date Range"),
                                        Paragraph(text=""),  # spacing hack
                                        Paragraph(text=""),
                                        date_select, country_select])

    vboxsmall = VBoxModelForm(_children=[controls, source_par])
    #hbox1 = HBox(children=[job_loc_plot_builder(), vboxsmall])
    #hbox2 = HBox(children=[weekday_builder(), jobtype_builder()])
    #layout = VBox(children=[hbox1, hbox2])
    layout = VBox(children=[vboxsmall])

    return layout

obj = layout()
document.add(obj)
update_data()

if __name__ == "__main__":
    link = session.object_link(obj)
    print("Please visit %s to see the plots" % link)
    try:
        while True:
            session.load_document(document)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print()
    except ConnectionError:
        print("Connection to bokeh-server was terminated")
