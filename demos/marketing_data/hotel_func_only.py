import json
import numpy
from collections import OrderedDict, defaultdict
from bokeh.sampledata import us_states, us_counties, unemployment
from bokeh.plotting import *

us_states = us_states.data.copy()
us_counties = us_counties.data.copy()

import numpy as np
import pandas as pd

from bokeh.charts import Histogram, show, output_file


del us_states["HI"]
del us_states["AK"]

state_xs = [us_states[code]["lons"] for code in us_states]
state_ys = [us_states[code]["lats"] for code in us_states]

county_xs=[us_counties[code]["lons"] for code in us_counties if us_counties[code]["state"] not in ["ak", "hi", "pr", "gu", "vi", "mp", "as"]]
county_ys=[us_counties[code]["lats"] for code in us_counties if us_counties[code]["state"] not in ["ak", "hi", "pr", "gu", "vi", "mp", "as"]]

#colors = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]
colors = ["#E8F6F6", "#B3ECEC", "#89ECDA", "#43E8D8", "#40E0D0", "#3BD6C6"]

cnty_st_to_id = {}
ratings_per_county = defaultdict(list)
for county_id in us_counties:
    if us_counties[county_id]["state"] in ["ak", "hi", "pr", "gu", "vi", "mp", "as"]:
        continue
    cnty_st_to_id[(us_counties[county_id]['name'].lower(), us_counties[county_id]['state'].upper())] = county_id

zip_to_county = {}
zip_to_state = {}

has_reviews = 0
has_ratings = 0
has_postalCode = 0
good_ones = 0

all_ratings = []


with open("US.txt") as f:
    lines = f.readlines()
    for line in lines:
        data = line.split('\t')
        zip_to_county[data[1]] = data[5]
        zip_to_state[data[1]] = data[4]


def make_usa_plot():
    lines1 = [json.loads(line) for line in open('/Users/talumbau/Downloads/115_1.txt')]
    lines2 = [json.loads(line) for line in open('/Users/talumbau/Downloads/115_2.txt')]

    def normalize_county(c):
        c = c.lower()
        c = c.replace("saint", "st.")
        idx = c.find(' (city)')
        if idx > -1:
            c = c[:idx]
        idx = c.find(' (city')
        if idx > -1:
            c = c[:idx]
        idx = c.find(' county')
        if idx > -1:
            c = c[:idx]
        if c == "la salle":
            c = "lasalle"
        if c == 'do\xc3\xb1a ana':
            c = "dona ana"
        return c
    

    def normalize_zip(z):
        idx = z.find('-')
        if idx > -1:
            z = z[:idx]
        idx = z.find('.')
        if idx > -1:
            z = z[:idx]
        return z
    

    def normalize_rating(r):
        try:
            idx = r.find('/')
        except AttributeError:
            #Assume it's a list
            if r:
                return numpy.mean(map(float, r))
            else:
                print "broken: ", r
                return None

        if idx > -1:
            return r[:idx]
        else:
            return r

    def scale_rating(r):
        if r > 5.0:
            return r/2.
        else:
            return r
    

    def ave_rating(reviews):
        tot = 0
        count = 0
        for rev in reviews:
            if 'rating' in rev:
                count += 1
                r = normalize_rating(rev['rating'])
                tot += float(r)
        if tot:
            return tot/count
        else:
            return None

    def count(lines):
        global has_reviews
        global has_postalCode
        global good_ones
        global has_ratings
        global all_ratings
        for h in lines:
            has_location = False
            if 'reviews' in h:
                has_reviews += 1
                ave = ave_rating(h['reviews'])
                if ave:
                    #print "ave rating is ", ave
                    has_ratings += 1
                    all_ratings.append(ave)
            if 'postalCode' in h:
                has_postalCode += 1
                #us_result = geonameszip.lookup_postal_code(h['postalCode'], 'US')
                z = normalize_zip(h['postalCode'])
                if z in zip_to_county:
                    county = zip_to_county[z]
                    state = zip_to_state[z]
                    #print "county, state: ", county, state
                    has_location = True
                    if not (normalize_county(county), state) in cnty_st_to_id:
                        if not state in ["AK", "HI"]:
                            print "couldn't look up ", county, state
                            print "next"
                    else:
                        if ave:
                            county_id = cnty_st_to_id[(normalize_county(county), state)]
                            ratings_per_county[county_id].append(ave)

                else:
                    print "couldn't find: ", z
            if 'reviews' in h and 'postalCode' in h and has_location:
                good_ones += 1

    count(lines1)
    count(lines2)

    print "has_reviews: ", has_reviews
    print "has_ratings: ", has_ratings
    print "has_postalCode: ", has_postalCode
    print "good_ones: ", good_ones
    print "total: ", len(lines1) + len(lines2)
    print "ratings per county", len(ratings_per_county)

    county_colors = []
    for county_id in us_counties:
        if us_counties[county_id]["state"] in ["ak", "hi", "pr", "gu", "vi", "mp", "as"]:
            continue
        try:
            all_ratings = ratings_per_county[county_id]
            print "all ratings", all_ratings
            if all_ratings:
                ave_for_county = scale_rating(numpy.mean(all_ratings))
                idx = int(6./5.*ave_for_county - 1.0)
                county_colors.append(colors[idx])
            else:
                county_colors.append("black")
        except KeyError:
            county_colors.append("black")

    output_file("choropleth_hotels.html", title="hotel ratings example")

    #p = figure(title="Average Hotel Ratings", toolbar_location="left",
    #    plot_width=1100, plot_height=700)
    #toolset = "crosshair,pan,reset,resize,save,wheel_zoom"
    #p = figure(title="Average Hotel Ratings", tools=toolset,
    #           plot_width=800, plot_height=500)

    p.patches(county_xs, county_ys, fill_color=county_colors, fill_alpha=0.7,
        line_color="white", line_width=0.5)
    p.patches(state_xs, state_ys, fill_alpha=0.0,
        line_color="#884444", line_width=2)

    return p

"""distributions = OrderedDict(ratings=all_ratings)
# create a pandas data frame from the dict
df = pd.DataFrame(distributions)
distributions = df.to_dict()
output_file("ratings_hist.html")

hist = Histogram(df, bins=50, legend=True)

show(hist)"""

