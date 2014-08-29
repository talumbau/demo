# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""Emp Util
Provides some functions for translating country names in employee dataset
"""

import os
PRINT_LOCATION_ERRORS = os.environ.get("PRINT_LOCATION_ERRORS", True)
"""
    Some mappings for pre-processing the data
"""
c2i = {}
i2c = {}
count = 0

c2i['Argentina'] = count
i2c[count] = 'Argentina'
count += 1

c2i['Chile'] = count
i2c[count] = 'Chile'
count += 1

c2i['Mexico'] = count
i2c[count] = 'Mexico'
count += 1

c2i['Spain'] = count
i2c[count] = 'Spain'
count += 1

c2i['Venezuela'] = count
i2c[count] = 'Venezuela'
count += 1

c2i['Honduras'] = count
i2c[count] = 'Honduras'
count += 1

c2i['Italy'] = count
i2c[count] = 'Italy'
count += 1

c2i['Puerto Rico'] = count
i2c[count] = 'Puerto Rico'
count += 1

c2i['Singapore'] = count
i2c[count] = 'Singapore'
count += 1

c2i['Costa Rica'] = count
i2c[count] = 'Costa Rico'
count += 1

c2i['Bolivia'] = count
i2c[count] = 'Bolivia'
count += 1

c2i['Portugal'] = count
i2c[count] = 'Portugal'
count += 1

c2i['Cuba'] = count
i2c[count] = 'Cuba'
count += 1

c2i['Germany'] = count
i2c[count] = 'Germany'
count += 1

c2i['Angola'] = count
i2c[count] = 'Angola'
count += 1

c2i['Vietnam'] = count
i2c[count] = 'Vietnam'
count += 1

c2i['Philippines'] = count
i2c[count] = 'Philippines'
count += 1

c2i['Malaysia'] = count
i2c[count] = 'Malaysia'
count += 1

c2i['Germany'] = count
i2c[count] = 'Germany'
count += 1

c2i['Belgium'] = count
i2c[count] = 'Belgium'
count += 1

c2i['Australia'] = count
i2c[count] = 'Australia'
count += 1

c2i['Canada'] = count
i2c[count] = 'Canada'
count += 1

c2i['France'] = count
i2c[count] = 'France'
count += 1

c2i['Indonesia'] = count
i2c[count] = 'Indonesia'
count += 1

c2i['Colombia'] = count
i2c[count] = 'Colombia'
count += 1

c2i['Ecuador'] = count
i2c[count] = 'Ecuador'
count += 1

c2i['Russia'] = count
i2c[count] = 'Russia'
count += 1

c2i['Guatemala'] = count
i2c[count] = 'Guatemala'
count += 1

c2i['El Salvador'] = count
i2c[count] = 'El Salvador'
count += 1

c2i['Panama'] = count
i2c[count] = 'Panama'
count += 1

c2i['Uruguay'] = count
i2c[count] = 'Uruguay'
count += 1

c2i['Peru'] = count
i2c[count] = 'Peru'
count += 1

c2i['China'] = count
i2c[count] = 'China'
count += 1

c2i['Brazil'] = count
i2c[count] = 'Brazil'
count += 1

c2i['Islands'] = count
i2c[count] = 'Islands'
count += 1

c2i['United States'] = count
i2c[count] = 'United States'
count += 1

c2i['Dominican Republic'] = count
i2c[count] = 'Dominican Republic'
count += 1

c2i['Paraguay'] = count
i2c[count] = 'Paraguay'
count += 1

c2i['Saint Martin'] = count
i2c[count] = 'Saint Martin'
count += 1

c2i["Côte d'Ivoire"] = count
i2c[count] = "Côte d'Ivoire"
count += 1

c2i['Dubai'] = count
i2c[count] = 'Dubai'
count += 1

c2i['Romania'] = count
i2c[count] = 'Romania'
count += 1

c2i['United Kingdom'] = count
i2c[count] = 'United Kingdom'
count += 1

c2i['Other'] = count
i2c[count] = 'Other'

# Mapping strings in Locations to countries


def make_tuples(seq, val):
    return [(i, val) for i in seq]

ctry_to_names = []
ctry_to_names.extend(make_tuples(('buenos aires', 'aires', 'argentina'),
                     'Argentina'))
ctry_to_names.append(('chile', 'Chile'))
ctry_to_names.extend(make_tuples(('m\xc3\xa9xico', 'mexica', 'méxico',
                     'mxico', 'yucat\xc3\xa1n', 'yucatn', 'mexico',
                                  'zaragoza', 'extranjeros'), 'Mexico'))
ctry_to_names.extend(make_tuples(('españa', 'espaa', 'spain'), 'Spain'))
ctry_to_names.append(('venezuela', 'Venezuela'))
ctry_to_names.append(('honduras', 'Honduras'))
ctry_to_names.extend(make_tuples(('italia', 'italy'), 'Italy'))
ctry_to_names.append(('puerto rico', 'Puerto Rico'))
ctry_to_names.append(('rico', 'Puerto Rico'))
ctry_to_names.append(('singapore', 'Singapore'))
ctry_to_names.append(('rica', 'Costa Rica'))
ctry_to_names.append(('bolivia', 'Bolivia'))
ctry_to_names.append(('portugal', 'Portugal'))
ctry_to_names.append(('cuba', 'Cuba'))
ctry_to_names.append(('alemania', 'Germany'))
ctry_to_names.append(('angola', 'Angola'))
ctry_to_names.append(('vietnam', 'Vietnam'))
ctry_to_names.append(('filipinas', 'Philippines'))
ctry_to_names.extend(make_tuples(('malaysia', 'malasia'), 'Malaysia'))
ctry_to_names.append(('germany', 'Germany'))
ctry_to_names.append(('belgium', 'Belgium'))
ctry_to_names.append(('australia', 'Australia'))
ctry_to_names.extend(make_tuples(('canad', 'ontario'), 'Canada'))
ctry_to_names.extend(make_tuples(('france', 'francia'), 'France'))
ctry_to_names.append(('indonesia', 'Indonesia'))
ctry_to_names.append(('colombia', 'Colombia'))
ctry_to_names.append(('ecuador', 'Ecuador'))
ctry_to_names.append(('rusia', 'Russia'))
ctry_to_names.append(('guatemala', 'Guatemala'))
ctry_to_names.append(('el salvador', 'El Salvador'))
ctry_to_names.append(('salvador', 'El Salvador'))
ctry_to_names.extend(make_tuples(('panama', 'panamá', 'panam'), 'Panama'))
ctry_to_names.append(('uruguay', 'Uruguay'))
ctry_to_names.extend(make_tuples(('perú', 'per', 'peru'), 'Peru'))
ctry_to_names.append(('china', 'China'))
ctry_to_names.extend(make_tuples(('brazil', 'brasil', 'iguaz', 'iguazú',
                     'patagonia'), 'Brazil'))
ctry_to_names.extend(make_tuples(('barbados', 'camern', 'tierra del fuego',
                     'fuego', 'camerún', 'martn'), 'Islands'))
ctry_to_names.extend(make_tuples(('san luis, misuri', 'florida', 'california',
                     'eeuu', 'usa'), 'United States'))
ctry_to_names.extend(make_tuples(('dominicana', 'dominican', 'repblica',
                     'domingo'), 'Dominican Republic'))
ctry_to_names.append(('república dominicana', 'Dominican Republic'))
ctry_to_names.append(('paraguay', 'Paraguay'))
ctry_to_names.append(('martin', 'Saint Martin'))
ctry_to_names.extend(make_tuples(('martin', 'mart\xc3\xadn'), 'Saint Martin'))
ctry_to_names.append(('ivoire', "Côte d'Ivoire"))
ctry_to_names.extend(make_tuples(('dubai', 'dubái', 'dubi'), 'Dubai'))
ctry_to_names.extend(make_tuples(('romania', 'rumania'), 'Romania'))
ctry_to_names.extend(make_tuples(('united kingdom', 'reino', 'liverpool'),
                                 'United Kingdom'))

all_countries = dict(ctry_to_names)
count = 1


def get_country(x):
    global count
    """Auxilary function to return name of country"""
    for nme in x.lower().split():
        name_str = str(nme.strip(' ,'))
        if name_str in all_countries:
            return all_countries[name_str]
    else:
        if PRINT_LOCATION_ERRORS:
            print "Unknown location! "+x
        return "Other"


def get_byte_for_country(x):
    country = get_country(x)
    return c2i[country]


def get_country_for_byte(x):
    return i2c[x]


def job_type_mapper(job):
    if u'Medio' in job:
        return "Half Time"
    if u'Completo' in job:
        return "Full Time"
    if u'Horas' in job:
        return "Hourly"
    if u'Tempora' in job:
        return "Temporary"
    return "Other"

"""
   Mapper function for pre-processing job type
"""

j2b = {}
b2j = {}

j2b['Half Time'] = 0
b2j[0] = 'Half Time'

j2b['Full Time'] = 1
b2j[1] = 'Full Time'

j2b['Hourly'] = 2
b2j[2] = 'Hourly'

j2b['Temporary'] = 3
b2j[3] = 'Temporary'

j2b['Other'] = 4
b2j[4] = 'Other'


def get_byte_for_jobtype(x):
    jt = job_type_mapper(x)
    return j2b[jt]


def get_jobtype_for_byte(x):
    return b2j[x]


def number_yr_from_month_yr(month_and_yr):
    dates = {"January": "01",
             "February": "02",
             "March": "03",
             "April": "04",
             "May": "05",
             "June": "06",
             "July": "07",
             "August": "08",
             "September": "09",
             "October": "10",
             "November": "11",
             "December": "12"}

    _1, _2 = month_and_yr.split()
    return dates[_1], _2
