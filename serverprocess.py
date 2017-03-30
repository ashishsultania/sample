import os, subprocess, requests,sys, json, time
from datetime import datetime
from subprocess import Popen, PIPE
import httplib,ssl

global basedir


def read_in():
    lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])


#filename = read_in()
filename = "regular_log_2017-03-30-11-15-16-882747.tar"
homedir  = os.path.expanduser("~")
basedir =  homedir + '/sample'
uploaddir = basedir + '/uploadserver'
os.chdir(uploaddir)
a, b = filename.split('.')

cmd = "mkdir " + a
p = Popen([cmd], stdin=PIPE, shell=True)

cmd = "tar xf " +  filename + " -C " + a
os.system(cmd)

target = open("output.txt", 'w')
target.write("COMMAND DONE")  

path = uploaddir+ '/' + a + '/'
subdirectories = os.listdir(path)
if 'home' in subdirectories:
    path =  path + 'home'
    subdirectories = os.listdir(path)
    #print("1",subdirectories)
    while len(subdirectories) == 1:
        path = path + '/' +  subdirectories[0]
        subdirectories = os.listdir(path)
        #print("2",subdirectories)
#print subdirectories

path = path + '/' + subdirectories[ subdirectories.index("sample")] + '/otherlogs'
print path
os.chdir(path)

print (os.getcwd())


target.write(os.getcwd())  



with open("wmctrl.log") as f:
    for line in f:
        #print line
        if "Mozilla" in line:
             print "Mozilla is running"
             a = line.split(' ')
             mozilla_win_id = a[0]
             print mozilla_win_id
f.close()

hex_int = int(mozilla_win_id, 16)
mozilla_win_id = hex(hex_int)

with open("activeterminal.log") as f:
    active_win_id_dec = f.readlines()
f.close()

result = [int(x.strip(' "')) for x in active_win_id_dec]
active_win_id_dec =  hex(result[0])


if active_win_id_dec != mozilla_win_id:
    print("Not Equal")
    cmd = "xkill -id "+active_win_id_dec
    #send_out(cmd)

    target.write(active_win_id_dec)  


    ssl._create_default_https_context = ssl._create_unverified_context
    web = httplib.HTTPSConnection('192.168.242.136:8081')
    print web
#headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    web.request("GET", "/?cmd=1:"+cmd)
    r1 = web.getresponse()

    print r1.status, r1.reason, r1.read()


    target.write(r1.read())  
    target.close()

             


































