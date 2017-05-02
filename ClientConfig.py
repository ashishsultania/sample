import os

serverurl = 'https://130.233.193.124:8082/upload'  #Check ifconfig of server
basedir  = os.path.expanduser("~")
dirnm =  basedir + '/sample'
ethpath = 'enp0s25' #Check the path /sys/class/net/enp0s25

id1="ebc1a0ec1ab04c39a84586a0b33160c4\n" #/var/lib/dbus/machine-id
id2="5b947643beea4a919805f1f4f332ea76\n"
readonly_pos="2" # Readonly OS position number starting from 0
reboot_count = 3
networkcheck_st = 300 #in seconds
log_interval = 30 #in seconds
loglevel = 10     # CRITICAL = 50, ERROR = 40, WARNING = 30, INFO = 20, DEBUG = 10, NOTSET = 0

