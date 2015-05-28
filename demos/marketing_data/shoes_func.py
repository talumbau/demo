import json
import re
import collections
import numpy as np
from bokeh.sampledata.iris import flowers
from bokeh.plotting import *
import bokeh
import itertools
import pandas as pd

all_brands = set()
all_mns = set()
all_lens = set()
num_mans = 0
num_mannums = 0
num_prices = 0
num_brands = 0
goodones = []
has_prices = 0
lines1 = [json.loads(line) for line in open('116_1.txt')]
lines2 = [json.loads(line) for line in open('116_2.txt')]
all_ps = []

def extract_full_price(r):
    if 'price' in r:
        p = r['price']
    else:
        p = r['salePrice']

    return extract_price(p)


def extract_price(p):
    p = p.strip()
    p = re.sub('[,&?#]', '', p)
    if p.startswith("USD"):
        p = p[3:]
    p = p.strip()
    if p.startswith("GBP"):
        p = p[3:]
    if p.startswith("AUD"):
        p = p[3:]
    p = p.strip()
    p = p.strip()
    if not p:
        return 0.0
    try:
        return float(p)
    except ValueError:
        print "this is no good: ", p
        idx = p.find('.')
        try:
            return float(p[:idx+3])
        except ValueError:
            print "this is also no good: ", p
            if ';' in p:
                p = p[p.find(';')+1:]
            return float(p[:idx+3])

def collect(lines):
    global num_mans
    global num_mannums
    global num_prices
    global num_brands
    for x in lines:
        if 'manufacturer' in x:
            num_mans += 1
        if 'manufacturerNumber' in x:
            num_mannums += 1
            all_mns.add(x['manufacturerNumber'])
        if 'prices' in x:
            num_prices += 1
        if 'brand' in x:
            num_brands += 1
            all_brands.add(x['brand'].lower())
        if 'prices' in x and 'brand' in x:
            goodones.append(x)


def price_is_good(r):

    if 'price' in r['prices'][0] or 'salePrice' in r['prices'][0]:
        return True
    else:
        return False

def get_all_shoes():
    thelines = (json.loads(line) for line in open('/Users/talumbau/Downloads/116_1.txt'))
    #lines2 = [json.loads(line) for line in open('/Users/talumbau/Downloads/116_2.txt')]
    return _get_all_shoes(thelines)


def _get_all_shoes(alllines):
    name = []
    price = []
    brand = []

    fields = ["name", "prices", "brand"]
    for x in alllines:
        checks = [f in x for f in fields]
        has_all = all(checks)
        if has_all and price_is_good(x):
            theprice = extract_full_price(x['prices'][0])
            thebrand = x['brand'].lower()
            name.append(x['name'])
            price.append(theprice)
            brand.append(thebrand)

    df = pd.DataFrame({'name':name, 'price':price, 'brand':brand})
    return df.loc[:1200, :]

def make_brands_to_prices(df):

    brands_to_prices = collections.defaultdict(list)
    #import pdb;pdb.set_trace()
    for idx, s in df.iterrows():
        brands_to_prices[s['brand'].lower()].append(s['price'])

    return brands_to_prices


def get_brands_to_prices():

    global has_prices
    brands_to_prices = collections.defaultdict(list)

    collect(lines1)
    collect(lines2)

    for count, d in enumerate(goodones):
        all_lens.add(len(d['prices']))
        if 'price' in d['prices'][0]:
            all_ps.append(extract_price(d['prices'][0]['price']))
            theprice = extract_price(d['prices'][0]['price'])
            brands_to_prices[d['brand'].lower()].append(theprice)
            has_prices += 1
        elif 'salePrice' in d['prices'][0]:
            all_ps.append(extract_price(d['prices'][0]['salePrice']))
            theprice = extract_price(d['prices'][0]['salePrice'])
            brands_to_prices[d['brand'].lower()].append(theprice)
            has_prices += 1
        else:
            print "can't find price or salePrice: ", count

    print "num_mans: ", num_mans
    print "num_mannums: ", num_mannums
    print "num_prices: ", num_prices
    print "num_brands: ", num_brands
    print "total: ", len(lines1)
    print "total lines2: ", len(lines2)
    print "goodones: ", len(goodones)
    print "all_brands: ", len(all_brands)
    print "all_mns: ", len(all_mns)
    print "all_lens: ", all_lens
    print "has_prices: ", has_prices

    return brands_to_prices

def average_price_per_brand(b2p):
    aves = [ (np.mean(prices), b) for b, prices in b2p.iteritems()]
    return sorted(aves)

def split_on_prices(prices_and_brands, splits):
    import collections
    prices = [x[0] for x in prices_and_brands]
    idxs = np.digitize(prices, splits)
    groups = collections.defaultdict(list)
    for idx, pb in zip(idxs, prices_and_brands):
        groups[splits[idx]].append(pb)

    return groups
    
def make_brand_to_color(groups):
    colors = bokeh.palettes.Spectral11
    price_points = sorted(groups.keys())
    #def ave_price(somelist):
        #return np.mean([x[0] for x in somelist])
    #ave_prices = sorted([ (k, ave_price(v)) for k,v in groups.iteritems()])
    #import pdb;pdb.set_trace()
    price2idx = {r:p for p,r in zip(range(len(price_points)), price_points)}
    b2c = {}
    for price, brands in groups.iteritems():
        for b in brands:
            b2c[b[1]] = colors[price2idx[price]]

    return b2c

def min_max_range(ranges, prices):
    """take a list of prices and give back the ranage within 'ranges' that
       we should use for plotting
    """
    _min = len(ranges) + 1
    _max = -1
    for p in prices:
        idx = p//100
        if idx < _min:
            _min = idx
        if idx > _max:
            _max = idx
    return int(_min), int(_max)


