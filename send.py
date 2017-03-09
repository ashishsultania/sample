#!/usr/bin/python3

import requests

url = 'https://192.168.242.128:8081/upload'
files = {'logFile': open('send.csv', 'rb')}
r = requests.post(url, files=files,verify=False)
