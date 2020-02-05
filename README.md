Dradis-CSV-Data-Import (https://govanguard.com)
==
[![Build Status](https://travis-ci.com/GoVanguard/dradis-csv-data-import.svg?branch=master)](https://travis-ci.com/GoVanguard/dradis-csv-data-import)
[![Known Vulnerabilities](https://snyk.io/test/github/GoVanguard/dradis-csv-data-import/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/GoVanguard/dradis-csv-data-import?targetFile=requirements.txt)
[![Maintainability](https://api.codeclimate.com/v1/badges/96f876225bd0bf4c8519/maintainability)](https://codeclimate.com/github/GoVanguard/dradis-import-cve-details/maintainability)

# About csv-data-import-dradis
Imports issues, nodes, evidence and notes with custom fields from a CSV file into Dradis projects via RestAPI. If the Nodes already exist then new Notes or Evidence will be added to the existing Node.

## Installation

```
git clone https://github.com/GoVanguard/csv-data-import-dradis.git
```

## Recommended Python Version:

csv-data-import-dradis currently supports **Python 3**.

* The recommened version for Python 3 is **3.6.x** or higher.

## Dependencies:

csv-data-import-dradis depends on the `requests`, `csv` and `argparse` python modules.

Each module can be installed independently as shown below.

#### Requests Module (http://docs.python-requests.org/en/latest/)

- Install for Windows:
```
c:\python27\python.exe -m pip install requests
```

- Install for Ubuntu/Debian:
```
sudo apt-get install python-requests
```

- Install for Centos/Redhat:
```
sudo yum install python-requests
```

- Install using pip on Linux:
```
sudo pip install requests
```

#### csv Module 

- Install for Windows:
```
c:\python27\python.exe -m pip install csv
```

- Install for Ubuntu/Debian:
```
sudo apt-get install csv  
```

- Install using pip:
```
sudo pip install csv
```

#### argparse Module

- Install for Ubuntu/Debian:
```
sudo apt-get install python-argparse
```

- Install for Centos/Redhat:
```
sudo yum install python-argparse
``` 

- Install using pip:
```
sudo pip install argparse
```

## Script Configuration

### Dradis API
For Dradis REST API information go to: https://dradisframework.com/pro/support/guides/rest_api/

### CSV File
The CSV file must be saved in **UTF-8** format. The first row of the CSV file must be the column names/headings. A 'title' heading  is required for all import types. A 'node_name' heading required for Nodes w/evidence imports & Nodes w/Note imports. Nodes w/Evidence requires an 'issue_id' heading in your CSV. The heading order and case does not matter. The other headings and data will become text in your Issues, Notes, and Evidence. The easiest way to create a CSV file is to create a table in Excel and then save it as a CSV.

#### Issues CSV Example  
Title,Impact,Ease,CVSS,Summary  
SSL Broken,Low,Low,0,Bad SSL  
Firewall Broken,Medium,Medium,5,Bad Firewall  
Server Broken,Low,Medium,7,BadServer  

#### Nodes with Notes CSV Example
Node_Name,Title,Impact,Ease,CVSS,Summary  
google.com,SSL Broken,Low,Low,0,Bad SSL  
askjeeves.com,Firewall Broken,Medium,Medium,5,Bad Firewall  
bing.com,Server Broken,Low,Medium,7,BadServer  

#### Nodes with Evidence CSV Example  
Node_Name,Title,Impact,Ease,CVSS,Summary,Issue_id  
google.com,SSL Broken,Low,Low,0,Bad SSL,23  
askjeeves.com,Firewall Broken,Medium,Medium,5,Bad Firewall,24  
bing.com,Server Broken,Low,Medium,7,BadServer,25  

## Usage

Short Form        | Long Form      | Description
----------------- | -------------- |-------------
-i                | --issue        | Import CSV data into Issues
-n                | --nodenote     | Import CSV data into Nodes and Notes.
-e                | --nodeevidence | Import CSV data into Nodes and Evidence.
-h                | --help         | show the help message and exit
CSV filename      | <--Required    | .csv filename
Dradis URL        | <--Required    | Dradis URL
Dradis Project ID | <--Required    | Dradis Project ID
Dradis API Token  | <--Required    | Dradis API token


### Examples

* To see the usage syntax use -h switch:

```python csvtodradis.py -h```

* To import into Issues:

``python csvtodradis.py -i filename.csv https://dradis-pro.dev 6 1234567abc``

* To import into Nodes and Notes:

``python csvtodradis.py -n filename.csv https://dradis-pro.dev 6 1234567abc``

* To To import into Nodes and Evidence:

``python csvtodradis.py -e filename.csv https://dradis-pro.dev 6 1234567abc``


## License

csv-data-import-dradis is licensed under the GNU Affero General Public License v3.0. Take a look at the [LICENSE](https://github.com/GoVanguard/csv-data-import-dradis/blob/master/LICENSE) for more information.

## Version
**Current version is 1.0**
