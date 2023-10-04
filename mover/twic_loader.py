from urllib.error import HTTPError
import os, zipfile
from urllib.request import urlparse, urlretrieve
import requests, time

HTTP_ERROR = int(404)

