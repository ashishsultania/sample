import io
import os
import sys
import json
import time
import shutil
import signal
import logging
import requests
import logmanage
import ServerConfig

from subprocess import Popen, PIPE

global cmdlist


def sendmail(TO,body,subject):
    # Import smtplib for the actual sending function
    import smtplib

    From2 = 'SERVER'
    # Prepare actual message
    msg = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (From2,"".join(TO), subject, body)
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(ServerConfig.smtp_con)
    s.ehlo()
    s.starttls()
    s.login(ServerConfig.FROM,ServerConfig.password)
    s.sendmail(ServerConfig.FROM, [TO], msg)
    s.quit()


def entercmd(cmd):
    global cmdlist
    
    logging.debug(cmd)
    
    cmdlist.append(cmd)
    
def sendcmd(pid):
    global cmdlist
    
    os.chdir(ServerConfig.basedir)
    
    
    device_str = {}
    device_str['cmd'] = cmdlist

    logging.debug("returning data" + json.dumps(device_str) )

    with open('cmdfile.json', 'w') as f:
        json.dump(device_str, f, indent = 4, ensure_ascii=False)

    f.close()

    os.kill(int(pid), signal.SIGUSR2)
    


def runfirefox():
    cmd = "firefox " + ServerConfig.CURRENT_URL
    entercmd(cmd)
        
    cmd = "wmctrl -r mozilla -b add,fullscreen"
    entercmd(cmd)
    if "youtube.com" in ServerConfig.CURRENT_URL:
        cmd = "xdotool key F"
        entercmd(cmd)

def checkhdmicable():

    colorflag       = 1
    vgaconnect      = 0
    ddcc_support    = 1
    templist        = []
    
    with open("xrandr.log") as f:
        for line in f:
            #logging.debug(line)
            if " connected" in line:
                vgaconnect = 1
    f.close()
    
    if vgaconnect == 0:
        logging.debug("Sending Mail")
        sendmail(ServerConfig.clientemail, "Please check connection cable manually.\n \n Admin","Display Device Cable disconnected")
    else:
        found_abstract = False
        with open("ddccontrol.log") as f2:
            for line2 in f2:
                if "Color settings" in line2:
                    logging.debug("Color setting present")
                    colorflag = 0
                    break
                if 'No monitor supporting DDC/CI available' in line2:
                    ddcc_support = 0
                    break
        f2.close()

        with open("ddccontrol.log") as f2:
            for line2 in f2:
                if 'Power' in line2:
                    found_abstract = True
                if found_abstract:
                    if 'address' in line2:
                        templist = line2.split(',')
        f2.close()
        
        #TODO: This will not affect the variable value
        for data in templist:
            if 'address' in data:
                ServerConfig.displayaddr = (data.split('=')[1])
                logging.debug(ServerConfig.displayaddr)    
        
    
        #Case of Monitor is powered off
        logging.debug(colorflag)
        logging.debug(ddcc_support)
        if colorflag == 1 and ddcc_support == 1:  
            cmd = "ddccontrol -p -r "+ServerConfig.displayaddr+" -w 1" 
            entercmd(cmd)
            
            
def managedb(uploaddir,logfolder):
    os.chdir(uploaddir)
    shutil.rmtree(logfolder)
    
    logging.debug("Calling main() of logmanage")
    logmanage.main()


def main(argv):
    
    global cmdlist

    cmdlist = []
    pid = sys.argv[2]
    logging.debug(pid)
    filename = (sys.argv[1])
    logging.debug(filename)
    
    uploaddir = ServerConfig.basedir + '/uploadserver'
    os.chdir(uploaddir)
    a, b = filename.split('.tar')
    
    cmd = "mkdir " + a
    p = Popen([cmd], stdin=PIPE, shell=True)
    p.wait()

    cmd = "tar -xzf " +  filename + " -C " + a
    p = Popen([cmd], stdin=PIPE, shell=True)
    p.wait()
    
    mpath = uploaddir+ '/' + a + '/'
    for path, subdirs, files in os.walk(mpath):
        for name in subdirs:
            c = path.count('sample')
            if name == 'sample':
                tpath = path + "/" + name
                break     
    
    path = tpath + '/otherlogs'
    os.chdir(path)
    
    logging.debug(os.getcwd())
    moz_run = 0
    with open("wmctrl.log") as f:
        for line in f:            
            if ServerConfig.defaultapp in line:
                logging.debug("Mozilla is running")
                win_id = line.split(' ')
                mozilla_win_id = win_id[0]
                logging.debug(mozilla_win_id)
                moz_run = 1
    f.close()
    if moz_run == 0:
        #Default app is not running
        runfirefox()
        
        checkhdmicable()
        #managedb(uploaddir,a)
        logging.debug("Calling sendcmd()" );
        sendcmd(pid)
        

        
        
        logging.debug("Calling exit()" );
        sys.exit(0)
                

    hex_int = int(mozilla_win_id, 16)
    mozilla_win_id = hex(hex_int)
    
    with open("activeterminal.log") as f:
        active_win_id_dec = f.readlines()
    f.close()
    
    with open("currenturl.log") as f:
        current_url = f.readlines()
    f.close()
    
    
    result = [int(x.strip(' "')) for x in active_win_id_dec]
    active_win_id_dec =  hex(result[0])
    
    
    if active_win_id_dec != mozilla_win_id:
        logging.debug("Not Equal")
        cmd = "xkill -id "+active_win_id_dec
        logging.debug(active_win_id_dec)  
        entercmd(cmd)
            
        
    # check the size of browser
    if active_win_id_dec == mozilla_win_id: 
        logging.debug("Active window is mozilla")   
        with open("xwininfo.log") as f:
            logging.debug("Reading xwininfo.log")
            for line in f:                
                if "geometry" in line:             
                    desktop_geom = ((line.split(' ')[3].rstrip()).split('+')[0].split('x'))
                if ServerConfig.defaultapp in line:
                    mozilla_browser_geom = (line.split(' ')[-3].split('+')[0].split('x'))
                    x = int(line.split(' ')[-1].split('+')[1].rstrip())
                    y = int(line.split(' ')[-1].split('+')[2].rstrip())
                    logging.debug("x="+str(x)+",y="+str(y))
                    if len(current_url) > 1:
                        logging.debug("Length of current url is" + str(len(current_url)))
                        if ServerConfig.CURRENT_URL != current_url[int(current_url[0].rstrip())].rstrip():
                            logging.debug("Current URL is not equal to Default")
                            logging.debug("Current URL:"+ServerConfig.CURRENT_URL)
                            logging.debug("Running one is:"+current_url[int(current_url[0].rstrip())].rstrip())
                            cmd = "xkill -id "+active_win_id_dec
                            entercmd(cmd)
                            
                            runfirefox()
                                
                if "Chrome" in line:
                    chrome_browser_geom = (line.split(' ')[-3].split('+')[0].split('x'))
        f.close()
       
    
    
        if x != 0 or y!=0:
            logging.debug("Toolbar enabled")
            cmd = "gsettings set org.compiz.unityshell:/org/compiz/profiles/unity/plugins/unityshell/ launcher-hide-mode 1"
            entercmd(cmd)
    
     
        if int(desktop_geom[0])*int(desktop_geom[1]) > int(mozilla_browser_geom[0])*int(mozilla_browser_geom[1]):
            #cmd = "wmctrl -r mozilla -b add,fullscreen"
            cmd = "xdotool key F11"
            entercmd(cmd)
    
    checkhdmicable()

    managedb(uploaddir,a)
    
    sendcmd(pid)
    
    

    


if(__name__ == "__main__"):
    logging.basicConfig(filename='serverlog.txt', filemode='w', level=ServerConfig.loglevel, format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s() - %(message)s')
    main(sys.argv)

