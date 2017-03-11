import os,thread, subprocess, requests,sys, threading,json
from datetime import datetime
from subprocess import Popen, PIPE



def startserver( ):
    cmd = "node server_clientside.js"
    p = Popen([cmd], stdin=PIPE, shell=True)
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
    
                
if(__name__ == "__main__"):
    main()
    
    
