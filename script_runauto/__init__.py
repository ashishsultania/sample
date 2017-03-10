import os,sys
import subprocess
from datetime import datetime
import os.path
import thread
from subprocess import Popen, PIPE



def startserver( threadName):
    cmd = "node server.js"
    p = Popen([cmd], stdin=PIPE, shell=True)
    p.communicate(input='Help_ind1a')
    print("done")

    

os.chdir('/home/sultana1/sample')
thread.start_new_thread( startserver, ("Thread-1", ) )


input_v = input("Enter 1:cmd or 2:file:")
if input_v == 1:
    cmd = "ls"   # command to be run
    failure = os.system(cmd)
    
    if failure:
        print( "Execution of failed!")

if input_v == 2:
    fname =  raw_input("Enter script file name: ")
    print(fname)
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
    
    
os.chdir('/home/sultana1/sample')
timformat='%Y-%m-%d-%H:%M:%S.%f'
tim=datetime.now().strftime(timformat)

with open("script_output" + tim + ".txt","a") as f:
    f.write(output)  
f.close()