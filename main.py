import os, requests, threading,time,sys
from datetime import datetime
from subprocess import Popen, PIPE
import memuse
import json
import ClientConfig
import reboot_script
import logging


def invokepostclient (filename):
    files = {'logFile': open(filename, 'rb')}
    r = requests.post(ClientConfig.serverurl, files=files,verify=False)
    logging.debug("Response from post is: " + str(r))

def runcommad(cmd):
    p = Popen([cmd], stdin=PIPE, shell=True)
    (output, err) = p.communicate()
    ## Wait for date to terminate. Get return returncode ##
    p_status = p.wait()
    logging.debug("Output is: " + str(output))
    logging.error("Error is: " + str(err)) 
    logging.debug("Status is: " + str(p_status))   
    
def startserver():
    serverfname = ClientConfig.dirnm + '/server_clientside.js'
    if not os.path.isfile(serverfname):
        print("File no Exist: Exiting Server Thread......")
        sys.exit()
    print(serverfname)   

    os.chdir(ClientConfig.dirnm)
    cmd = "node server_clientside.js"
    p = Popen([cmd], stdin=PIPE, shell=True)
    #cmd = "sudo node server_clientside.js"
    #os.system(cmd)
    time.sleep(2)

    #print("Server stared done")


def checknetwork():
    while 1:
        f = open("/sys/class/net/"+ClientConfig.ethpath+"/carrier", "r")
        try:
            if "0\n" ==    f.read():
                logging.debug("Calling reboot script as eth cable is not connected")
                reboot_script.main()
                
                time.sleep(ClientConfig.networkcheck_st)
        except IOError:
            cmd = "ifconfig "+ClientConfig.ethpath+" up"
            runcommad(cmd)
            logging.debug("Calling reboot script as eth is down")
            reboot_script.main()
            time.sleep(30)

def getcurrent_url():
    logging.debug("Checking URL")
    mozdir = ClientConfig.basedir + '/.mozilla/firefox/'
    target = open("otherlogs/currenturl.log", 'w')

    tabs = []
    active_urlindex = 0
    for root, dirs, files in os.walk(mozdir):
        for name in dirs:
            if name.endswith('.default'):
                filepath = os.path.join(mozdir, name)
                filepath = filepath + '/sessionstore-backups'
                for root, dirs, files in os.walk(filepath):
                    for name in files:
                        if name == 'recovery.js':                                            
                            f = open(filepath + "/"+name, "r")
                            jdata = json.loads(f.read())
                            f.close()
                            active_urlindex= str(jdata["windows"][0]["selected"])
                            target.write(active_urlindex + "\n")

                            tabs.append(active_urlindex)
                            
                            for win in jdata.get("windows"):
                                for tab in win.get("tabs"):
                                    i = tab.get("index") - 1
                                    tabs.append(tab.get("entries")[i].get("url"))
                                    target.write(str(tab.get("entries")[i].get("url"))+ "\n")
                target.close()

                return(tabs)
    target.close()        
    return("Mozilla is closed: recovery.js not exist")


def main():
        
    logging.info("Starting main file")
    #TODO: Remove sleep 5
    time.sleep(5)
    
    if not os.path.isdir(ClientConfig.dirnm):
        os.mkdir(ClientConfig.dirnm)
    os.chdir(ClientConfig.dirnm)
    logging.debug ("Working Directory:" + os.getcwd())
    
    t           = threading.Thread(target=startserver)
    t.daemon    = True

    t1          = threading.Thread(target=checknetwork)
    t1.daemon   = True
    logging.debug ("Check internal Network in a thread:" + t1.name)
    t1.start()
    logging.debug ("Start Server in a thread:" + t.name)
    t.start()

    #Create all the logs from the commands
    otherlogdir =  ClientConfig.dirnm + '/otherlogs/'
    if not os.path.isdir(otherlogdir):
        os.mkdir(otherlogdir)
    logging.debug ("Working Directory:" + os.getcwd())
    
    
    while 1:
        logging.debug ("Inside While")
        os.chdir(ClientConfig.dirnm)
        logging.debug ("Working Directory:" + os.getcwd())
        
        logging.debug ("Getting current URL")
        getcurrent_url()
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
            runcommad(cmd[i])
            
        memuse.getmemuse(ClientConfig.dirnm + '/otherlogs/memuse')
        
        #Create periodic logs
        timformat='%Y-%m-%d-%H-%M-%S-%f'
        tim=datetime.now().strftime(timformat)
        foldername = "regular_log_" + tim
        filename = foldername +".tar"
        time.sleep(5)
        plogdir =  ClientConfig.dirnm + '/periodic_log'
        if not os.path.isdir(plogdir):
            os.mkdir(plogdir)
        os.chdir(plogdir)
        fname = ['/var/log/kern.log',
                 '/var/log/syslog',
                 '/var/log/Xorg.0.log',
                 '/var/log/auth.log',
                 '/etc/rsyslog.conf',
                 '/var/log/wtmp',
                 '/var/log/btmp',
                 '/var/run/utmp',
                 '/var/log/gpu-manager.log',
                 '/var/log/journal/',
                 ClientConfig.basedir +'/.mozilla/firefox/Crash\ Reports/',
                 ClientConfig.basedir +'/sample/otherlogs/'
                 ]
        cmd = "tar cPf "+ filename  + " " + fname[0]

        runcommad(cmd)     

        
        for i in range(len(fname)-1):
            cmd = "tar uPf " + filename + " " + (fname[i+1])
            runcommad(cmd)
        
        cmd = "gzip "+filename
        runcommad(cmd)   
        
        
        invokepostclient(filename+".gz")
        time.sleep(10)
        
        os.remove(filename+".gz")
        
        time.sleep(ClientConfig.log_interval)
        
                
if(__name__ == "__main__"):
    logging.basicConfig(filename='clientlog.txt', filemode='w', level=ClientConfig.loglevel, format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s() - %(message)s')
    main()
    
    
