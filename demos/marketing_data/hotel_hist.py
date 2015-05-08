import json
import numpy
from collections import OrderedDict

import numpy as np
import pandas as pd

from bokeh.charts import Histogram, show, output_file


lines1 = [json.loads(line) for line in open('/Users/talumbau/Downloads/115_1.txt')]
lines2 = [json.loads(line) for line in open('/Users/talumbau/Downloads/115_2.txt')]

has_reviews = 0
has_ratings = 0
has_postalCode = 0
good_ones = 0

all_ratings = []

def normalize_rating(r):
    try:
        idx = r.find('/')
    except AttributeError:
        import pdb;pdb.set_trace()
        #Assume it's a list
        return numpy.mean(map(float, r))

    if idx > -1:
        return r[:idx]
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
    for h in lines:
        if 'reviews' in h:
            has_reviews += 1
            ave = ave_rating(h['reviews'])
            if ave:
                print "ave rating is ", ave
                has_ratings += 1
                all_ratings.append(ave)
        if 'postalCode' in h:
            has_postalCode += 1
        if 'reviews' in h and 'postalCode' in h:
            good_ones += 1

count(lines1)
count(lines2)

print "has_reviews: ", has_reviews
print "has_ratings: ", has_ratings
print "has_postalCode: ", has_postalCode
print "good_ones: ", good_ones
print "total: ", len(lines1) + len(lines2)

distributions = OrderedDict(ratings=all_ratings)
# create a pandas data frame from the dict
df = pd.DataFrame(distributions)
distributions = df.to_dict()
output_file("ratings_hist.html")

hist = Histogram(df, bins=50, legend=True)

show(hist)

