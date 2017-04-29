import os, subprocess, requests,sys, json, time
from datetime import datetime
from subprocess import Popen, PIPE
import httplib,ssl

global basedir
global displayaddr

def read_in():
    lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])

def sendmail(TO,body,subject):
    # Import smtplib for the actual sending function
    import smtplib

    # Import the email modules we'll need
    from email.mime.text import MIMEText
    FROM = 'ankitkumdel@gmail.com'
    password='helloaalto'
    From2 = 'SERVER'
    # Prepare actual message
    msg = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (From2,"".join(TO), subject, body)
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.ehlo()
    s.starttls()
    s.login(FROM,password)
    s.sendmail(FROM, [TO], msg)
    s.quit()

CURRENT_URL = "https://www.youtube.com/watch?v=3ZbZppJI-sA"
displayaddr = '0xd6'
filename = read_in()
#filename = "regular_log_2017-04-24-11-58-42-397202.tar"
homedir  = os.path.expanduser("~")
basedir =  homedir + '/sample'
uploaddir = basedir + '/uploadserver'
os.chdir(uploaddir)
a, b = filename.split('.')

cmd = "mkdir " + a
p = Popen([cmd], stdin=PIPE, shell=True)
p.wait()
cmd = "tar xf " +  filename + " -C " + a
os.system(cmd)

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
        if "Mozilla" in line:
            print "Mozilla is running"
            a = line.split(' ')
            mozilla_win_id = a[0]
            print mozilla_win_id
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
    print("Not Equal")
    cmd = "xkill -id "+active_win_id_dec
    #send_out(cmd)

    target.write(active_win_id_dec)  


    #ssl._create_default_https_context = ssl._create_unverified_context
    url = 'https://192.168.242.136:8081/?cmd=1:' + cmd
    r = requests.get(url,verify=False)
    print r.text
             

    target.close()
    
    
# check the size of browser
if active_win_id_dec == mozilla_win_id: 
    print "Active window is mozilla"   
    with open("xwininfo.log") as f:
        for line in f:
            #print line
            if "geometry" in line:             
                desktop_geom = ((line.split(' ')[3].rstrip()).split('+')[0].split('x'))
            if "Mozilla" in line:
                mozilla_browser_geom = (line.split(' ')[-3].split('+')[0].split('x'))
                x = int(line.split(' ')[-1].split('+')[1].rstrip())
                y = int(line.split(' ')[-1].split('+')[2].rstrip())
                if len(current_url) > 1:
                    if CURRENT_URL != current_url[int(current_url[0].rstrip())].rstrip():
                        cmd = "xkill -id "+active_win_id_dec
                        url = 'https://192.168.242.136:8081/?cmd=1:' + cmd
                        r = requests.get(url,verify=False)
                        
                        cmd = "firefox " + CURRENT_URL
                        url = 'https://192.168.242.136:8081/?cmd=1:' + cmd
                        r = requests.get(url,verify=False)
                        time.sleep(4)
                        cmd = "wmctrl -r mozilla -b add,fullscreen"
                        url = 'https://192.168.242.136:8081/?cmd=1:' + cmd
                        r = requests.get(url,verify=False)
                        if "youtube.com" in CURRENT_URL:
                            time.sleep(4)
                            cmd = "xdotool key F"
                            url = 'https://192.168.242.136:8081/?cmd=1:' + cmd
                            r = requests.get(url,verify=False)
                            
            if "Chrome" in line:
                chrome_browser_geom = (line.split(' ')[-3].split('+')[0].split('x'))
    f.close()
   



    if x != 0 or y!=0:
        print("Toolbar enabled")
        cmd = "gsettings set org.compiz.unityshell:/org/compiz/profiles/unity/plugins/unityshell/ launcher-hide-mode 1"
        #cmd = "ls -lrt"
        url = 'https://192.168.242.136:8081/?cmd=1:' + cmd
        r = requests.get(url,verify=False)

 
    if int(desktop_geom[0])*int(desktop_geom[1]) > int(mozilla_browser_geom[0])*int(mozilla_browser_geom[1]):
        #cmd = "wmctrl -r mozilla -b add,fullscreen"
        cmd = "xdotool key F11"
        url = 'https://192.168.242.136:8081/?cmd=1:' + cmd
        r = requests.get(url,verify=False)
        

colorflag = 0   
vgaconnect = 0
templist = []
with open("xrandr.log") as f:
    for line in f:
        print line
        if " connected" in line:
            vgaconnect = 1
f.close()

if vgaconnect == 0:
    print "Sending Mail"
    sendmail('ashishsultania2k7@gmail.com', "Please check connection cable manually.\n \n Admin","Display Device Cable disconnected")
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
    
    for data in templist:
        if 'address' in data:
            displayaddr = (data.split('=')[1])    
    

    #Case of Monitor is powered off
    if colorflag == 1:  
        cmd = "ddccontrol -p -r "+displayaddr+" -w 1" 
        print cmd               
        url = 'https://192.168.242.136:8081/?cmd=1:' + cmd
        r = requests.get(url,verify=False)
        #sendmail('ashishsultania2k7@gmail.com', "Please check your Display.\n \n Admin","Display Device Powered off")




































