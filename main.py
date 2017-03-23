import os, requests, threading,time,sys
from datetime import datetime
from subprocess import Popen, PIPE
import getpass

global pswd
global basedir

def invokepostclient (filename):
    url = 'https://192.168.242.137:8082/upload'
    files = {'logFile': open(filename, 'rb')}
    r = requests.post(url, files=files,verify=False)


def startserver():
    global pswd
    global basedir
    
    dirnm =  basedir + '/sample'
    serverfname = dirnm + '/server_clientside.js'
    if not os.path.isfile(serverfname):
        print("File no Exist: Exiting Server Thread......")
        sys.exit()
    print(serverfname)   

    os.chdir(dirnm)
    cmd = "node server_clientside.js"
    p = Popen([cmd], stdin=PIPE, shell=True)
    time.sleep(2)

    p.communicate(input=pswd)
    #print("Server stared done")




def main():
    #Start server at client side in a thread
    global pswd
    global basedir
    
    basedir = '/home/'+os.environ['USER']
    pswd = getpass.getpass('Password:')
    dirnm =  basedir + '/sample'
    if not os.path.isdir(dirnm):
        os.mkdir(dirnm)
    os.chdir(dirnm)
    
    t = threading.Thread(target=startserver)
    t.daemon = True
    t.start()
    #print ("Server loop running in thread:", t.name)
    #thread.start_new_thread( startserver, ("Thread-1",) )
    
    #Create all the logs from the commands
    otherlogdir =  dirnm + '/otherlogs'
    if not os.path.isdir(otherlogdir):
        os.mkdir(otherlogdir)
    os.chdir(otherlogdir)
    
    cmd = 'sudo powertop --csv=powertop_report.txt --time=5s'
    p = Popen([cmd], stdin=PIPE, shell=True)
    p.communicate(input=pswd)

    #Create periodic logs
    timformat='%Y-%m-%d-%H-%M-%S-%f'
    tim=datetime.now().strftime(timformat)
    filename = "regular_log_" + tim +".tar"
    time.sleep(5)
    plogdir =  dirnm + '/periodic_log'
    if not os.path.isdir(plogdir):
        os.mkdir(plogdir)
    os.chdir(plogdir)
    while 1:
        fname = ['/var/log/kern.log',
                 '/var/log/syslog',
                 '/var/log/syslog.1',
                 '/etc/rsyslog.conf',
                 '/proc/asound/cards',
                 '/proc/buddyinfo',
                 '/proc/loadavg',
                 '/proc/meminfo',
                 '/proc/partitions',
                 '/proc/stat',
                 '/proc/uptime',
                 '/proc/sys/kernel/',
                 '/var/log/wtmp',
                 '/var/log/btmp',
                 '/var/run/utmp',
                 '/var/log/wtmp.1',
                 '/home/'+os.environ['USER'] +'/.mozilla/firefox/Crash\ Reports/',
                 '/home/sultana1/sample/otherlogs/']
        cmd = "sudo tar cvPf "+ filename  + " " + fname[0]

        p = Popen([cmd], stdin=PIPE, shell=True)
        b = p.communicate(input=pswd)
            
        for i in range(len(fname)-1):
            cmd = "sudo tar uPf " + filename + " " + (fname[i+1])
            p = Popen([cmd], stdin=PIPE, shell=True)
            p.communicate(input=pswd)
                
        invokepostclient(filename)
        time.sleep(10)
                
if(__name__ == "__main__"):
    main()
    
    
