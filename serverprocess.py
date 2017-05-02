import os, requests,sys, json, time
from subprocess import Popen, PIPE
import httplib,ssl
import ServerConfig

def read_in():
    lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])

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


def invokepostserver_cmd1(cmd):
    url = ServerConfig.clienturl+'cmd=1:' + cmd
    r = requests.get(url,verify=False)


def runfirefox():
    cmd = "firefox " + ServerConfig.CURRENT_URL
    invokepostserver_cmd1(cmd)
    
    time.sleep(4)
    
    cmd = "wmctrl -r mozilla -b add,fullscreen"
    invokepostserver_cmd1(cmd)
    if "youtube.com" in ServerConfig.CURRENT_URL:
        time.sleep(4)
        cmd = "xdotool key F"
        invokepostserver_cmd1(cmd)

def checkhdmicable():

    colorflag = 0   
    vgaconnect = 0
    templist = []
    with open("xrandr.log") as f:
        for line in f:
            #print line
            if " connected" in line:
                vgaconnect = 1
    f.close()
    
    if vgaconnect == 0:
        #print "Sending Mail"
        sendmail(ServerConfig.clientemail, "Please check connection cable manually.\n \n Admin","Display Device Cable disconnected")
    else:
        found_abstract = False
        with open("ddccontrol.log") as f2:
            for line2 in f2:
                if "Color settings" not in line:
                    colorflag = 1
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
        
    
        #Case of Monitor is powered off
        if colorflag == 1:  
            cmd = "ddccontrol -p -r "+ServerConfig.displayaddr+" -w 1" 
            invokepostserver_cmd1(cmd)



def main():

    filename = read_in()
    #filename = "regular_log_2017-05-02-14-18-23-754872.tar.gz"
    
    uploaddir = ServerConfig.basedir + '/uploadserver'
    os.chdir(uploaddir)
    a, b = filename.split('.tar')
    
    cmd = "mkdir " + a
    p = Popen([cmd], stdin=PIPE, shell=True)
    p.wait()

    cmd = "tar -xzf " +  filename + " -C " + a
    p = Popen([cmd], stdin=PIPE, shell=True)
    p.wait()
    
    target = open("output.txt", 'w')
    target.write("COMMAND DONE")  
    
    mpath = uploaddir+ '/' + a + '/'
    target.write(mpath)
    for path, subdirs, files in os.walk(mpath):
        for name in subdirs:
            c = path.count('sample')
            if c == 2:
                tpath = path
                break     
    
    path = tpath + '/otherlogs'
    target.write(path)
    os.chdir(path)
    
    print (os.getcwd())
    
    
    target.write(os.getcwd())  
    
    
    
    with open("wmctrl.log") as f:
        for line in f:
            #print line
            if ServerConfig.defaultapp in line:
                #print "Mozilla is running"
                a = line.split(' ')
                mozilla_win_id = a[0]
                #print mozilla_win_id
            else:
                #Default app is not running
                runfirefox()
                checkhdmicable()
                return
                
    f.close()
    
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
        #print("Not Equal")
        cmd = "xkill -id "+active_win_id_dec
        target.write(active_win_id_dec)  
        invokepostserver_cmd1(cmd)
    
        target.close()
        
        
    # check the size of browser
    if active_win_id_dec == mozilla_win_id: 
        #print "Active window is mozilla"   
        with open("xwininfo.log") as f:
            for line in f:
                #print line
                if "geometry" in line:             
                    desktop_geom = ((line.split(' ')[3].rstrip()).split('+')[0].split('x'))
                if ServerConfig.defaultapp in line:
                    mozilla_browser_geom = (line.split(' ')[-3].split('+')[0].split('x'))
                    x = int(line.split(' ')[-1].split('+')[1].rstrip())
                    y = int(line.split(' ')[-1].split('+')[2].rstrip())
                    if len(current_url) > 1:
                        if ServerConfig.CURRENT_URL != current_url[int(current_url[0].rstrip())].rstrip():
                            cmd = "xkill -id "+active_win_id_dec
                            invokepostserver_cmd1(cmd)
                            
                            runfirefox()
                                
                if "Chrome" in line:
                    chrome_browser_geom = (line.split(' ')[-3].split('+')[0].split('x'))
        f.close()
       
    
    
        if x != 0 or y!=0:
            print("Toolbar enabled")
            cmd = "gsettings set org.compiz.unityshell:/org/compiz/profiles/unity/plugins/unityshell/ launcher-hide-mode 1"
            invokepostserver_cmd1(cmd)
    
     
        if int(desktop_geom[0])*int(desktop_geom[1]) > int(mozilla_browser_geom[0])*int(mozilla_browser_geom[1]):
            #cmd = "wmctrl -r mozilla -b add,fullscreen"
            cmd = "xdotool key F11"
            invokepostserver_cmd1(cmd)
    
    checkhdmicable()
    
    
    


if(__name__ == "__main__"):
    main()





























