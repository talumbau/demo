import json
import numpy
from collections import OrderedDict, defaultdict
import itertools

import numpy as np
import pandas as pd

zip_to_state = {}
zip_to_county = {}
with open("US.txt") as f:
    lines = f.readlines()
    for line in lines:
        data = line.split('\t')
        zip_to_state[data[1]] = data[4]
        zip_to_county[data[1]] = data[5]

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

def state_is_good(hblob):
    z = normalize_zip(hblob['postalCode'])
    if z in zip_to_state:
        state = zip_to_state[z]
        if not state in ["AK", "HI"]:
            return True
        else:
            return False
    else:
        return False


def read_data(num_lines=-1):
    if num_lines < 0:
        unlimited = True
    else:
        unlimited = False

    lines1 = (json.loads(line) for line in open('/Users/talumbau/Downloads/115_1.txt'))
    lines2 = (json.loads(line) for line in open('/Users/talumbau/Downloads/115_2.txt'))
    alllines = itertools.chain.from_iterable([lines1, lines2])

    static_cols = ["city", "name", "lat", "long", "postalCode", "reviews"]
    saved_cols = ["city", "name", "lat", "long", "postalCode"]
    derived_cols = ["ave_review", "id", "num_reviews"]

    columns = {"city":[], "county":[], "name":[], "lat":[], "long":[],
            "id":[], "state":[], "ave_review":[], "num_reviews":[],
            'postalCode':[]}

    #the_reviews = {}
    the_reviews = []
    for count, h in enumerate(alllines):

        checks = [c in h for c in static_cols]
        has_all = all(checks)
        if has_all and state_is_good(h) and len(h['reviews']) > 0:
            for c in saved_cols:
                columns[c].append(h[c])

            ave = scale_rating(ave_rating(h['reviews']))
            columns['ave_review'].append(ave)
            z = normalize_zip(h['postalCode'])
            columns['state'].append(zip_to_state[z])
            columns['county'].append(zip_to_county[z])
            columns['id'].append(count)
            revs_with_text = [r['text'] for r in h['reviews'] if 'text' in r]
            #the_reviews[count] = revs_with_text
            the_reviews.append(revs_with_text)
            columns['num_reviews'].append(len(revs_with_text))
            if len(the_reviews) == 405:
                import pdb;pdb.set_trace()
           

        if not unlimited:
            if count > num_lines:
                break

    columns['lat'] = list(map(float, columns['lat']))
    columns['lon'] = list(map(float, columns['long']))

    return columns, the_reviews

dta, revs = read_data(num_lines=4000)
