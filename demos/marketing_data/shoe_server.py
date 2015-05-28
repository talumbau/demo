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

import shoes_app
from shoes_app import _shoedf
from shoes_app import ShoeApp
from bokeh.embed import components


app = Flask('sampleapp')

bokeh_url = "http://localhost:5006"
applet_url = "http://localhost:5050"


@app_document("shoe_example", bokeh_url)
def make_shoe_applet():
    app = ShoeApp.create()
    return app


@app.route("/")
def applet():
    print("stuff here")
    applet = make_shoe_applet()
    return render_template(
        "shoes.html",
        app_url = bokeh_url + "/bokeh/jsgenerate/VBox/ShoeApp/ShoeApp",
        app_tag = applet._tag,
    )


@app.route("/shoes", methods=['GET'])
def some_shoes():
    print("getting stuff here")
    _id = request.args.get('id','')
    report = ""
    bdf = _shoedf[ _shoedf['brand'] == _id]
    if len(bdf) > 0:
        report += "<h2>Product list for: " + str(bdf.iloc[0]['brand'])
        report += "</h2><br>"
    for idx, s in bdf.iterrows():
        report += str(s['name']) + " : " + str(s['price']) + " <br>"


    return report 




if __name__ == "__main__":
    print("\nView this example at: %s\n" % applet_url)
    app.debug = True
    app.run(host='0.0.0.0', port=5050)
