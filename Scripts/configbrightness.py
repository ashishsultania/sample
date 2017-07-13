#!/usr/bin/python3

import requests, ServerConfig

filename = 'configbrightness.sh'
clienturl   = 'https://'+ ServerConfig.serverip + ':' + ServerConfig.serverport + '/upload'

files = {'logFile': open(filename, 'rb')}
try:
    r = requests.post(clienturl, files=files,verify=False)
    print("Response from post is: " + str(r))
except:
    print("Connection refused to send log: " + filename)
    pass
