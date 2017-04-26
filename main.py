import os, requests, threading,time,sys
from datetime import datetime
from subprocess import Popen, PIPE
import memuse

global basedir

def invokepostclient (filename):
    url = 'https://192.168.242.139:8082/upload'
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
    #cmd = "sudo node server_clientside.js"
    #os.system(cmd)
    time.sleep(2)

    #print("Server stared done")




def main():
        
    #Start server at client side in a thread
    global basedir
    time.sleep(15)
 
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
    while 1:
        os.chdir(dirnm)
        print(os.getcwd())
        cmd = ['powertop --csv=otherlogs/powertop_report.txt --time=1s',
           'wmctrl -l > otherlogs/wmctrl.log',
           'xdotool getwindowfocus > otherlogs/activeterminal.log',
           'xwd -root -out otherlogs/filename.xwd',
           'xwininfo -root -all > otherlogs/xwininfo.log',
           'xrandr > otherlogs/xrandr.log',
           'ddccontrol -p > otherlogs/ddccontrol.log',
           'lshw > otherlogs/lshw.log',
           'convert -scale 100% -compress JPEG otherlogs/filename.xwd otherlogs/filename.jpeg'
           ]
        for i in range(len(cmd)-1): 
            #os.system(cmd[i])
            #if 'ddccontrol' in cmd[i]:
            #    time.sleep(5)
            p = Popen([cmd[i]], stdin=PIPE, shell=True)
            p.wait()

        memuse.getmemuse(dirnm + '/otherlogs/memuse')
        
        #Create periodic logs
        timformat='%Y-%m-%d-%H-%M-%S-%f'
        tim=datetime.now().strftime(timformat)
        filename = "regular_log_" + tim +".tar"
        time.sleep(5)
        plogdir =  dirnm + '/periodic_log'
        if not os.path.isdir(plogdir):
            os.mkdir(plogdir)
        os.chdir(plogdir)
        fname = ['/var/log/kern.log',
                 '/var/log/syslog',
                 '/var/log/syslog.1',
                 '/etc/rsyslog.conf',
                 '/var/log/wtmp',
                 '/var/log/btmp',
                 '/var/run/utmp',
                 '/var/log/wtmp.1',
                 basedir +'/.mozilla/firefox/Crash\ Reports/',
                 basedir +'/sample/otherlogs/']
        cmd = "tar cvPf "+ filename  + " " + fname[0]

        p = Popen([cmd], stdin=PIPE, shell=True)
        p.wait()      
        for i in range(len(fname)-1):
            cmd = "tar uPf " + filename + " " + (fname[i+1])
            p = Popen([cmd], stdin=PIPE, shell=True)
            p.wait()    
        invokepostclient(filename)
        time.sleep(10)
                
if(__name__ == "__main__"):
    main()
    
    
