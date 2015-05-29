import json
from collections import defaultdict
from bokeh.palettes import Blues6, RdYlGn6
PALETTE = ['#ef4e4d', '#ef4e4d', '#14a1af', '#14a1af', '#743184', '#743184'] 
import numpy as np

def get_some_counties():
    #f = open('/Users/talumbau/Downloads/convert.json')

    fips = open("fips.csv")
    fips_data = [ln.split(",") for ln in fips.readlines()]
    fips_to_state = { str(int(f[1])):f[0] for f in fips_data}

    f = open('convert2.json')
    c = json.load(f)

    county_xs = []
    county_ys = []
    names_state = []
    state = []
    for i in range(0, len(c['features'])):
        coords = c['features'][i]['geometry']['coordinates'][0]
        county_xs.append([coord[0] for coord in coords])
        county_ys.append([coord[1] for coord in coords])
        fips = str(int(c['features'][i]['properties']['STATEFP']))
        name = c['features'][i]['properties']['NAME']
        names_state.append(name + "_" + fips_to_state[fips])
        state.append(fips_to_state[fips])

    #return county_xs, county_ys
    return dict(xs=county_xs, ys=county_ys, color=['white']*len(county_xs), names=names_state,
                state=state)


def color_counties(hdata, county_data):

    color_palette = PALETTE

    name_count = defaultdict(int)
    name_ratings = {}
    #['color', 'xs', 'state', 'ys', 'names']
    alpha_map = {}
    alphas = []
    colors = []
    for cnty, state, rating in zip(hdata['county'], hdata['state'], hdata['ratings']):
        name = cnty+"_"+state
        name_count[name] += 1
        if name in name_ratings:
            name_ratings[name] += rating
        else:
            name_ratings[name] = rating

    #Get the mean per county
    for name, rating in name_ratings.iteritems():
        name_ratings[name] = rating/name_count[name]

    max_count = max(name_count.values())
    for k,v in name_count.iteritems():
        #alphas.append(float(n)/max_count)
        ratio = float(v)/max_count
        if ratio > 0.3:
            fill = 0.90
        elif ratio > 0.15:
            fill - 0.8
        else:
            fill = 0.5
        alpha_map[k] = fill
    total = 0
    for name in county_data['names']:
        if name in alpha_map:
            alphas.append(alpha_map[name])
        else:
            #import pdb;pdb.set_trace()
            #print "can't find ", name
            total += 1
            alphas.append(0.0)

    print "COULDN'T FIND: ", total
    county_data['alpha'] = alphas

    #Get the cutoffs for each color
    #ratings = np.sort(np.array(hdata['ratings']))
    ratings = np.sort(np.array(name_ratings.values()))
    ratingbins = np.array_split(ratings, 6)
    cutoffs = [x[-1] for x in ratingbins]
    print "cutoffs are ", cutoffs
    for name in county_data['names']:
        if name in name_ratings:
            ave = name_ratings[name]
            for idx, cut in enumerate(cutoffs):
                if cut >= ave:
                    #print "the ave is ", ave, "so idx is ", idx
                    colors.append(color_palette[idx])
                    break
        else:
            colors.append(color_palette[0])


    county_data['thecolors'] = colors
    return "hello"

