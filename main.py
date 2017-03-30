import os, requests, threading,time,sys
from datetime import datetime
from subprocess import Popen, PIPE
import getpass

global basedir

def invokepostclient (filename):
    url = 'https://192.168.242.138:8082/upload'
    files = {'logFile': open(filename, 'rb')}
    r = requests.post(url, files=files,verify=False)


def startserver():
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

    #print("Server stared done")




def main():
    #Start server at client side in a thread
    global basedir
    
    basedir  = os.path.expanduser("~")
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
    otherlogdir =  dirnm + '/otherlogs/'
    if not os.path.isdir(otherlogdir):
        os.mkdir(otherlogdir)
    os.chdir(otherlogdir)
    print(os.getcwd())
    cmd = ['powertop --csv=powertop_report.txt --time=1s',
           'wmctrl -l > wmctrl.log',
           'xdotool getwindowfocus > activeterminal.log',
           'xwd -root -out filename.xwd',
           'convert -scale 100% -compress JPEG filename.xwd filename.jpeg'
           ]
    for i in range(len(cmd)-1): 
        p = Popen([cmd[i]], stdin=PIPE, shell=True)

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
                 basedir +'/.mozilla/firefox/Crash\ Reports/',
                 basedir +'/sample/otherlogs/']
        cmd = "tar cvPf "+ filename  + " " + fname[0]

        p = Popen([cmd], stdin=PIPE, shell=True)
            
        for i in range(len(fname)-1):
            cmd = "tar uPf " + filename + " " + (fname[i+1])
            p = Popen([cmd], stdin=PIPE, shell=True)
                
        invokepostclient(filename)
        time.sleep(10)
                
if(__name__ == "__main__"):
    main()
    
    
