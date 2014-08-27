# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
"""Emp module
This module loads the South American employment dataset. It grabs the data
from the EMP_DATA_DIR environment variable.
"""

import os
import glob
import codecs
from functools import partial
import datetime
from blaze import *
from blaze.compute.python import *
from blaze.data import CSV, Concat
from blaze.expr.table import TableSymbol, merge, By
import pandas as pd
import bcolz
import tables

from employment_utils import get_country, number_yr_from_month_yr, job_type_mapper

# Employment Data Directory and Schema
EMP_DATA_DIR = os.environ.get("EMP_DATA_DIR", '/Users/talumbau/data/all_employment/')

SCHEMA_SMALL = '''
  {Posted_Date: date,
   Job_Type: string,
   Translated_Location: string}
   '''.lower()

SCHEMA_PYTABLES = '''
   {fn_country: string,
   fn_date: string,
   job_type: uint8,
   location: uint8,
   posted_dow: uint8}
  '''.lower()

SCHEMA = '''
  {Posted_Date: date,
   Location_1: string,
   Location_2: string,
   Department: string,
   Title: string,
   Salary: string,
   Start: string,
   Duration: string,
   Job_Type: string,
   Applications: string,
   Company: string,
   Contact: string,
   Phone: string,
   Fax: string,
   Translated_Location: string,
   Latitude: float32,
   Longitude: float32,
   Date_First_Seen: date,
   URL: string,
   Date_Last_Seen: date}
   '''.lower()


country_map = {"Argentina":'ar', "Mexico":'mx', "Colombia":'co', "Peru":'pe', "Dominican Republic":'do'}

bytesfile=tables.open_file("all_jobs_data.h5")
bytestab = bytesfile.root.test.sample
finalbig = pd.DataFrame.from_records(bytestab[:])
tbig = TableSymbol('employment', schema=SCHEMA_PYTABLES)
def get_jobs_between_dates_pytables_bytes(startdate, enddate, country=None):
    t = TableSymbol('employment', schema=SCHEMA_PYTABLES)
    tsel = t[t['fn_country'] == country_map[country]]
    start = ''.join(map(lambda x: str(x).zfill(2), [startdate.year, startdate.month, startdate.day]))
    end = ''.join(map(lambda x: str(x).zfill(2), [enddate.year, enddate.month, enddate.day]))
    jobs = tsel[ (tsel['fn_date'] > start) & (tsel['fn_date'] < end) ]
    final = into(pd.DataFrame, compute(jobs, {t:finalbig}))

    fdow = by(jobs, jobs['posted_dow'], jobs['posted_dow'].count())
    dowdf= into(pd.DataFrame, compute(fdow, {t:final}))
    floc = by(jobs, jobs['location'], jobs['posted_dow'].count())
    locdf= into(pd.DataFrame, compute(floc, {t:final}))
    ftyp = by(jobs, jobs['job_type'], jobs['posted_dow'].count())
    typdf= into(pd.DataFrame, compute(ftyp, {t:final}))

    return dowdf, locdf, typdf, len(final)


def _main_runner():
    """Prints table of employment durations.

Usage: emp.py <mon year>

   where <mon year> can look like "January 2013"
   set EMP_DATA_DIR to direcory including the employment files.

Example:

       EMP_DATA_DIR=~/workspace/data/employment/ python emp.py
    """
    if len(sys.argv) >= 2:
        print get_mean_job_data_from_date(" ".join(sys.argv[1:]))
    else:
        print _main_runner.__doc__


if __name__ == "__main__":
    _main_runner()
