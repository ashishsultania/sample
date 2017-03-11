import os,thread, subprocess, requests,sys, threading,json
from datetime import datetime


def invokepostclient (filename):
    url = 'https://192.168.242.1:8081/upload'
    files = {'logFile': open(filename, 'rb')}
    r = requests.post(url, files=files,verify=False)

def read_in():
    lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])

print("aa")
lines = read_in()
print("bb")
print(lines)

a, b = lines.split(':')

if a == '1':
    cmd = b   # command to be run
    failure = os.system(cmd)

    if failure:
        print( "Execution of failed!")
        os.chdir('/home/sultana1/sample')
    
    
elif a == '2':
    os.chdir('/home/sultana1/sample/uploadclient')
    fname = b
    os.path.isfile(fname) 
    failure = os.system("chmod +x "+ fname)
    if failure:
        print ("File name not exist or can't change the chmod!\n")
    
    cmd = "./"+fname

try:
    output = subprocess.check_output(cmd, shell=True,stderr=subprocess.STDOUT)
    print( "output",output)
   
except subprocess.CalledProcessError:
    print( 'Execution')
    sys.exit(1)
    
os.chdir('/home/sultana1/sample/result')
timformat='%Y-%m-%d-%H:%M:%S.%f'
tim=datetime.now().strftime(timformat)
filename = "script_output" + tim + ".txt"
with open(filename,"a") as f:
    f.write(output)  
f.close()
invokepostclient(filename)
#thread.start_new_thread( invokepostclient, ("Thread-1",filename) )




