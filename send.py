#!/usr/bin/python3

import requests

url = 'https://192.168.242.1:8081/upload'
files = {'logFile': open('tryscript.sh', 'rb')}
r = requests.post(url, files=files,verify=False)
