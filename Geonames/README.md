# bshGeonamesToADLS 
Containerized Python service which pulls geographic reference data from
[census.gov](https://www.census.gov/geographies/reference-files.2019.html) 
and [geonames.org](http://download.geonames.org/export/zip/). 

## Index
- Pandas and regex to data wrangle columns
    - [census_gov_ex.ipynb](jupyter/census_gov_ex.ipynb):
        - regex to implement advanced find/replace data wrangling on a 
        column
    - [geonames_ex.ipynb](jupyter/geonames_ex.ipynb):
        - `pandas.explode()` function to convert csv columns to rows
- Example [data model](db/scripts) 
using temporal tables and unicode columns with appropriate collation and
indexing

## Features
- Uses pandas and requests to download and transform data files
- Uses [`fastparquet`](https://pypi.org/project/fastparquet) and
[`python-snappy`](https://pypi.org/project/python-snappy) 
to save data sets in parquet format
- Uses [`azure-storage-file-datalake`](https://pypi.org/project/azure-storage-file-datalake) 
to write files to Azure data lake
- Uses [`azure-storage-queue`](https://pypi.org/project/azure-storage-queue/)
to read/write messages to Azure queue as a demonstration of the work
queue pattern
- Uses the [tenacity](https://tenacity.readthedocs.io/en/latest/) 
library for exponential retry of web requests
- Includes [scripts and configuration](aci/) to deploy to Azure Container
Instances

## Data Files
- Census.gov [reference files](https://www.census.gov/geographies/reference-files/2019/demo/popest/2019-fips.html) 
for US states
- Census.gov [Gazetteer files](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html) 
for counties
- Geonames.org extracts for [place names](https://download.geonames.org/export/dump/)
    - Additional [feature class](http://www.geonames.org/export/codes.html) descriptions
- Geonames.org extracts for [postal codes](http://download.geonames.org/export/zip/)