import os
import shutil
from datetime import datetime
from subprocess import Popen, PIPE
import sys,json

timformat='%Y-%m-%d %H:%M:%S.%f'
id1="f3829706e0e240d98c11f38266e63ee5\n"
id2="5b947643beea4a919805f1f4f332ea76\n"
id_tochange="3"

def ctime():
    global timformat
    timformat='%Y-%m-%d %H:%M:%S.%f'
    lines=datetime.now().strftime(timformat)
    return lines

def read_in():
    id_dbus=""
    global id_tochange

    with open("/var/lib/dbus/machine-id","r") as f:
        id_dbus = f.readline()
    f.close()
    print (id_dbus),type(id_dbus)
    print (id1),type(id1)

    if id_dbus == id1:
        os.chdir('/home/sultana1/sample')
        id_tochange = "1"
    elif id_dbus == id2:
        os.chdir('/mnt/home/sultana1/sample')
        id_tochange = "0"
    else:
        print "wrong id"
        exit(0)
def main():
    global id_tochange
    global timformat
    lines = ctime()
    read_in()
    with open("date.txt","a") as f:
        f.write(lines)

        f.write("\n")
    f.close()
    a=lines
    counter = 0
    for line in reversed(open("date.txt","r").readlines()):
        print( line.rstrip())
        b = datetime.strptime(a,timformat) - datetime.strptime(line.rstrip(),timformat)
        a = line.rstrip()
        if b.days == 0:
            if b.seconds > 10 and b.seconds < 23:
                print(b.seconds)
                counter=counter+1

    print("counter = ",counter)

    numlines = sum(1 for line in open('date.txt'))
    print numlines
    cmd = ['grub-set-default ','reboot','rm date.txt']
    if numlines == 3:
        p = Popen([cmd[0] + id_tochange], stdin=PIPE, shell=True)
        p.wait()
        p = Popen([cmd[1]], stdin=PIPE, shell=True)
    print id_tochange
    if id_tochange == "0":
        p = Popen([cmd[2]], stdin=PIPE, shell=True)
        p = Popen([cmd[0] + id_tochange], stdin=PIPE, shell=True)



if(__name__ == "__main__"):
    main()
