#!/usr/bin/python3

import requests

url = 'https://130.233.193.126:8081/upload'
files = {'logFile': open('shutdowndisp.sh', 'rb')}
r = requests.post(url, files=files,verify=False)
