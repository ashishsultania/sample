#!/usr/bin/python3

import requests, ServerConfig

url = ServerConfig.clienturl+'/save'

files = {'logFile': open('ClientConfigNew.py', 'rb')}
r = requests.post(url, files=files,verify=False)

