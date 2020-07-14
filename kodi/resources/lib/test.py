import json
import xml.etree.ElementTree as ET
from datetime import datetime
import urllib3
import certifi
from six.moves import html_parser
from bs4 import BeautifulSoup
from six.moves.urllib.parse import urlparse, parse_qs, urljoin

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where())

url = "http://data.jw-api.org/mediator/v1/categories/E/VODStudio?detailed=1&clientType=tvjworg"

categories = []
response = http.request('GET', url)
print(response.data)