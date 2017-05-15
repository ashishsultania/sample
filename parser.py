import os, subprocess, requests,sys, json
from datetime import datetime



def invokepostclient (filename,CConfig):
    files   = {'logFile': open(filename, 'rb')}
    r       = requests.post(CConfig.serverurl, files=files,verify=False)

def read_in():
    lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])

def send_out(cmd,CConfig):
    try:
        output = subprocess.check_output(cmd, shell=True,stderr=subprocess.STDOUT)
        #print( "output",output)
       
    except subprocess.CalledProcessError:
        #print( 'Execution')
        sys.exit(1)
        
    os.chdir(CConfig.dirnm + '/result')
    timformat='%Y-%m-%d-%H:%M:%S.%f'
    tim         = datetime.now().strftime(timformat)
    filename    = "script_output" + tim + ".txt"
    
    with open(filename,"a") as f:
        f.write(output)  
    f.close()
    
    invokepostclient(filename,CConfig)
    #thread.start_new_thread( invokepostclient, ("Thread-1",filename) )

def main():
    try:
        import ClientConfigNew as CConfig
    except:
        import ClientConfig as CConfig    

    lines   = read_in()
    a, b    = lines.split(':',1)
    
    #Run command
    if a == '1':
        cmd = b   # command to be run
        #failure = subprocess.Popen([cmd], stdin=PIPE, shell=True)
        #failure = subprocess.check_output(cmd, shell=True,stderr=subprocess.STDOUT)
        failure = os.system(cmd)
        if failure:
            os.chdir(CConfig.dirnm)
    
    #Sends specific file
    elif a == '3':
        file = b   # command to be run
        invokepostclient(file,CConfig)            
    
    #Run the script and send output
    elif a == '2':
        os.chdir(CConfig.dirnm + '/uploadclient')
        fname = b
        os.path.isfile(fname) 
        failure = os.system("chmod +x "+ fname)
        if failure:
            print ("File name not exist or can't change the chmod!\n")
        
        cmd = "./"+fname
        send_out(cmd,CConfig)


if(__name__ == "__main__"):
    main()


