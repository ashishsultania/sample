#!/usr/bin/python3

import requests

url = 'https://172.16.227.1:8081/save'
files = {'logFile': open('ClientConfigNew.py', 'rb')}
r = requests.post(url, files=files,verify=False)

