import os

serverurl = 'https://192.168.242.139:8082/upload'
basedir  = os.path.expanduser("~")
dirnm =  basedir + '/sample'
ethpath = '/sys/class/net/ens33/carrier'

id1="ebc1a0ec1ab04c39a84586a0b33160c4\n" #/var/lib/dbus/machine-id
id2="5b947643beea4a919805f1f4f332ea76\n"
readonly_pos="2" # Readonly OS position number starting from 0
reboot_count = 3
networkcheck_st = 30 #in seconds