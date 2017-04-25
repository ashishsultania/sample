#!/usr/bin/python3

import requests

url = 'https://130.233.193.223:8081/upload'
files = {'logFile': open('closedisplay.sh', 'rb')}
r = requests.post(url, files=files,verify=False)
