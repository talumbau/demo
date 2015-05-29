"""
This file demonstrates embedding a bokeh applet into a flask
application. See the README.md file in this dirrectory for
instructions on running.
"""
from __future__ import print_function

import logging
logging.basicConfig(level=logging.INFO)

from bokeh.pluginutils import app_document
from flask import Flask, render_template, request
import pandas as pd

import hotel_read
from combo_app import HotelApp, ShoeApp
from bokeh.embed import components
from bokeh.resources import CDN
import combo_app
from combo_app import _shoedf
from bokeh.embed import components



app = Flask('sampleapp')

bokeh_url = "http://localhost:5006"
applet_url = "http://localhost:5050"

hdata, hrevs = hotel_read.get_hotel_data()


@app_document("hotel_example", bokeh_url)
def make_hotel_applet():
    app = HotelApp.create()
    return app

@app_document("shoe_example", bokeh_url)
def make_shoe_applet():
    app = ShoeApp.create()
    return app

@app.route("/shoe_app")
def show_applet():
    print("stuff here")
    applet = make_shoe_applet()
    return render_template(
        "shoes.html",
        app_url = bokeh_url + "/bokeh/jsgenerate/VBox/ShoeApp/ShoeApp",
        app_tag = applet._tag,
    )



@app.route("/hotel_app")
def hotel_applet():
    print("stuff here")
    applet = make_hotel_applet()
    #dummy = make_dummy_applet(applet.pretext)
    print("stuff there")
    #parscript, div = components(applet.pretext, CDN)
    print("stuff everywhere")
    return render_template(
        "hotels.html",
        app_url = bokeh_url + "/bokeh/jsgenerate/VBox/HotelApp/HotelApp",
        app_tag = applet._tag,
        #dummy_tag = dummy._tag

    )

@app.route("/shoes", methods=['GET'])
def some_shoes():
    print("getting stuff here")
    _id = request.args.get('id','')
    report = ""
    bdf = _shoedf[ _shoedf['brand'] == _id]
    if len(bdf) > 0:
        report += "<h3>Product list for: " + str(bdf.iloc[0]['brand'])
        report += "</h3><br>"
    for idx, s in bdf.iterrows():
        report += str(s['name']) + " : " + str(s['price']) + " <br>"

    return report 


@app.route("/reviews", methods=['GET'])
def some_reviews():
    print("getting stuff here")
    _id = request.args.get('id','')
    rev = ""
    if _id:
        for i, r in enumerate(hrevs[int(_id)]):
            rev += "<h2>Review #%d: </h2> <br>" % (i + 1)
            rev += r + "<br>"

    return rev



if __name__ == "__main__":
    print("\nView this example at: %s\n" % applet_url)
    app.debug = True
    app.run(host='0.0.0.0', port=5050)
