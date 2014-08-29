## Prerequisites

This demo is configured to migrate data from TSV files to Postgres and MySQL databases. Instructions listed below are provided as guidance, and `brew`-specific commands are listed for the convenience of reproduction on OSX.

Install brew
`which -s brew || ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"`

Install postgres
`which -s psql || brew install postgresql`

Install psycopg2
`python -c 'import psycopg2' || pip install psycopg2`

### For mysql

```
which -s mysql || brew install mysql
python -c 'import MySQLdb' || pip install MySQL-python
```

### Blaze and Bokeh

`conda install blaze=0.6.1 bokeh=0.5.1`

## Configuration

Create database `employment`, with table `data`:

### Postgres

```
CREATE DATABASE employment;
\c employment
CREATE TABLE data ( posted_date DATE, location_1 TEXT,
location_2 TEXT, department TEXT, title TEXT, salary TEXT,
start TEXT, duration TEXT, job_type TEXT, applications TEXT,
company TEXT, contact TEXT, phone TEXT, fax TEXT,
translated_location TEXT, latitude FLOAT, longitude FLOAT,
date_first_seen DATE, url TEXT, date_last_seen DATE);
```

### MySQL

```
CREATE DATABASE employment;
USE employment;
CREATE TABLE data ( posted_date DATE, location_1 TEXT,
location_2 TEXT, department TEXT, title TEXT, salary TEXT,
start TEXT, duration TEXT, job_type TEXT, applications TEXT,
company TEXT, contact TEXT, phone TEXT, fax TEXT,
translated_location TEXT, latitude FLOAT, longitude FLOAT,
date_first_seen DATE, url TEXT, date_last_seen DATE);
```

## Running the Demo

The first cell in each notebook accepts a few references to data filepaths and database URLs, and should be configured before the rest of the notebook is run.
