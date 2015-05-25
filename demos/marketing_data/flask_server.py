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

import hotel_app
import hotel_read
from hotel_app import HotelApp
from bokeh.embed import components
from bokeh.resources import CDN


app = Flask('sampleapp')

bokeh_url = "http://localhost:5006"
applet_url = "http://localhost:5050"

hdata, hrevs = hotel_read.get_hotel_data()


@app_document("hotel_example", bokeh_url)
def make_hotel_applet():
    app = HotelApp.create()
    return app


@app.route("/")
def applet():
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

@app.route("/reviews", methods=['GET'])
def some_reviews():
    print("getting stuff here")
    _id = request.args.get('id','')
    rev = ""
    if _id:
        for i, r in enumerate(hrevs[int(_id)]):
            rev += "Review #%d: <br>" % (i + 1)
            rev += r + "<br>"

    return rev



if __name__ == "__main__":
    print("\nView this example at: %s\n" % applet_url)
    app.debug = True
    app.run(host='0.0.0.0', port=5050)
