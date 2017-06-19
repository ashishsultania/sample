#!/usr/bin/python3

import requests, ServerConfig

url = ServerConfig.clienturl+'/upload'
files = {'logFile': open('configbrightness.sh', 'rb')}
r = requests.post(url, files=files,verify=False)
