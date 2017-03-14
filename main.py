import os, requests, threading,time,getpass
from datetime import datetime
from subprocess import Popen, PIPE

def invokepostclient (filename):
    url = 'https://192.168.242.137:8082/upload'
    files = {'logFile': open(filename, 'rb')}
    r = requests.post(url, files=files,verify=False)


def startserver( ):
    os.chdir('/home/sultana1/sample')
    cmd = "node server_clientside.js"
    p = Popen([cmd], stdin=PIPE, shell=True)
    time.sleep(2)

    p.communicate(input='Help_ind1a')
    print("Server stared done")




def main():
    #Start server at client side in a thread
    os.chdir('/home/sultana1/sample')
    t = threading.Thread(target=startserver)
    t.daemon = True
    t.start()
    print ("Server loop running in thread:", t.name)
    #thread.start_new_thread( startserver, ("Thread-1",) )
    
    
    timformat='%Y-%m-%d-%H-%M-%S-%f'
    tim=datetime.now().strftime(timformat)
    filename = "regular_log_" + tim +".tar"
    time.sleep(5)
    print("now before while loop")
    while 1:
        os.chdir('/home/sultana1/sample/periodic_log')
        print("now in while loop")
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
                 '/var/log/wtmp.1']
        cmd = "sudo tar cvf "+ filename  + " " + fname[0]
        print(cmd)

        p = Popen([cmd], stdin=PIPE, shell=True)
        b = p.communicate(input='Help_ind1a')
        print(b)
            
        for i in range(len(fname)-1):
            cmd = "sudo tar uf " + filename + " " + (fname[i+1])
            p = Popen([cmd], stdin=PIPE, shell=True)
            p.communicate(input='Help_ind1a')
                
        invokepostclient(filename)
        time.sleep(10)
                
if(__name__ == "__main__"):
    main()
    
    
