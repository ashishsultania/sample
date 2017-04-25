import os, subprocess, requests,sys, json
from datetime import datetime

global basedir


def invokepostclient (filename):
    url = 'https://192.168.242.139:8082/upload'
    files = {'logFile': open(filename, 'rb')}
    r = requests.post(url, files=files,verify=False)

def read_in():
    lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])

def send_out(cmd):
    global basedir
    try:
        output = subprocess.check_output(cmd, shell=True,stderr=subprocess.STDOUT)
        print( "output",output)
       
    except subprocess.CalledProcessError:
        print( 'Execution')
        sys.exit(1)
        
    os.chdir(basedir + '/result')
    timformat='%Y-%m-%d-%H:%M:%S.%f'
    tim=datetime.now().strftime(timformat)
    filename = "script_output" + tim + ".txt"
    with open(filename,"a") as f:
        f.write(output)  
    f.close()
    invokepostclient(filename)
    #thread.start_new_thread( invokepostclient, ("Thread-1",filename) )

homedir  = os.path.expanduser("~")
basedir =  homedir + '/sample'

lines = read_in()

a, b = lines.split(':',1)

if a == '1':
    cmd = b   # command to be run
    #failure = subprocess.Popen([cmd], stdin=PIPE, shell=True)
    #failure = subprocess.check_output(cmd, shell=True,stderr=subprocess.STDOUT)
    	
    failure = os.system(cmd)
    #failure.wait()
    with open("filename.txt","a") as f:
        f.write(cmd)
        f.write('\n')
        f.write("%s\n" % failure)
        f.write('ashish')
    if failure:
        f.write( "Execution of failed!")
        os.chdir(basedir)
    #send_out(cmd)
    f.close()
    
elif a == '3':
    cmd = b   # command to be run
    invokepostclient(cmd)            

elif a == '2':
    os.chdir(basedir + '/uploadclient')
    fname = b
    os.path.isfile(fname) 
    failure = os.system("chmod +x "+ fname)
    if failure:
        print ("File name not exist or can't change the chmod!\n")
    
    cmd = "./"+fname
    send_out(cmd)





