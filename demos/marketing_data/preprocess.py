# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from blaze import *
from toolz.curried import *
import codecs
import glob
import os
from employment_utils import get_byte_for_country, get_byte_for_jobtype
from tables import *


# Define a record to characterize the Jobs
class Job(IsDescription):
    posted_dow = UInt8Col()
    job_type = UInt8Col()
    location = UInt8Col()
    fn_date = StringCol(20)
    fn_country = StringCol(2)

schema_csv = '''
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


@curry
def transform_chunk(name, chunk):
    """ Transform dynd array to what bcolz expects """
    # chunk[0] is the posted_date, chunk[1] is the job type,
    # chunk[2] is the location
    # name is the filename
    dow = chunk[0].weekday()
    jt = get_byte_for_jobtype(chunk[1])
    loc = get_byte_for_country(chunk[2])
    ans = (dow, jt, loc, name[-12:-4], name[-15:-13])
    return ans


EMP_DATA_DIR = os.environ.get("EMP_DATA_DIR",
                              '/Users/talumbau/data/all_employment/')
filenames = sorted(glob.glob(os.path.join(EMP_DATA_DIR,
                   'computrabajo-ar-20121106.tsv')))

filename = "all_jobs_data.h5"
# Open a file in "w"rite mode
h5file = open_file(filename, mode="w", title="Test file")
# Create a new group under "/" (root)
group = h5file.create_group("/", 'test', 'Employment information')
# Create one table on it
table = h5file.create_table(group, 'sample', Job, "Readout example")
# Create an index on the host site country
table.cols.fn_country.create_index()
# Create an index on the date the website was scanned
table.cols.fn_date.create_index()

ajob = table.row
lines = 0
print len(filenames)
for fname in filenames:
    print fname
    the_csv = CSV(fname, delimiter='\t', schema=schema_csv,
                  open=partial(codecs.open, encoding='utf-8',
                               errors='ignore'))
    dds = the_csv
    t = TableSymbol('employment', schema=schema_csv)
    # Filter out bad data
    tsel = t[t['translated_location'] != '']
    # Select out the desired columns
    jobs = tsel[['posted_date', 'job_type', 'translated_location']]
    # Specify data transformation
    dta = compute(jobs, {t: dds})
    chunks = (csv for csv in dta)
    data = map(transform_chunk(fname), chunks)
    for d in data:
        lines += 1
        if (lines % 100000 == 0):
            print lines

        ajob['fn_country'] = d[4]
        ajob['fn_date'] = d[3]
        ajob['location'] = d[2]
        ajob['job_type'] = d[1]
        ajob['posted_dow'] = d[0]
        # Insert a new record
        ajob.append()

# Close (and flush) the file
h5file.close()
