from datetime import datetime
from subprocess import Popen, PIPE
from socket import error as socket_error
from ws4py.client.threadedclient import WebSocketClient
from time import gmtime, strftime

import os
import sys
import json
import errno
import base64
import subprocess
import xml.etree.ElementTree as ET

global ws


class Client(WebSocketClient):

    def __init__(self, url, peer_id, protocols=None, extensions=None, heartbeat_freq=None, ssl_options=None, headers=None):
        super(Client, self).__init__(url, protocols, extensions, heartbeat_freq, ssl_options, headers)
        self.peer_id = peer_id

        
    #First time connection
    def opened(self):
        print("Client is up")
        
        device_str = {}
        device_str['content'] = "Hello"
        device_str['type'] = "Hello"
                
        self.send(json.dumps(device_str))
        
    def sendplog(self, filename):
        fo = open(filename,"rb")
        str_con = base64.b64encode(fo.read())
        device_str = {}
        device_str['content'] = str_con.decode('utf8')
        device_str['type'] = "tar.gz"
        device_str['filename'] = filename
        
        self.send(json.dumps(device_str))

    def send_out(self,cmd):
        try:
            output = subprocess.check_output(cmd, shell=True,stderr=subprocess.STDOUT)
            #print( "output",output)

        except subprocess.CalledProcessError:
            #print( 'Execution')
            sys.exit(1)

        timformat='%Y-%m-%d-%H:%M:%S.%f'
        tim         = datetime.now().strftime(timformat)
        filename    = "script_output" + tim + ".txt"

        
        device_str = {}
        device_str['content'] = output
        device_str['type'] = "out"
        device_str['filename'] = filename
        
        self.send(json.dumps(device_str))
        
        

    def closed(self, code, reason=None):
        print ("Closed down", code, reason)

    def received_message(self, m):
        try:
            import ClientConfigNew as CConfig
        except:
            import ClientConfig as CConfig   
        
        
        try:
            recv_str = m.data.decode('utf-8')
            msg = json.loads(recv_str)
            
            if self.validate_msg(msg):
                print (msg['type'])
            if msg['type'] == 'reportexe':
                #print("Command received:  " + msg['content'] + "at "+strftime("%Y-%m-%d %H:%M:%S", gmtime()))
                p = Popen([msg['content']], stdin=PIPE,stdout=PIPE, shell=True)
                (output, err) = p.communicate()
                print("Command executed successfully")
                
                timformat='%Y-%m-%d-%H:%M:%S.%f'
                tim         = datetime.now().strftime(timformat)
                filename    = "command_output" + tim + ".txt"
                
                device_str = {}
                device_str['content'] = output
                device_str['type'] = "outreportexe"
                device_str['filename'] = filename

                self.send(json.dumps(device_str))
                
            
                
            if msg['type'] == 'cmd':
                #print("Command received:  " + msg['content'] + "at "+strftime("%Y-%m-%d %H:%M:%S", gmtime()))
                p = Popen([msg['content']], stdin=PIPE, shell=True)
                #(output, err) = p.communicate()
                print("Command executed successfully")
            
            if msg['type'] == 'save':
                os.chdir(CConfig.dirnm + '/Client')
                print("Command to save file received")
                
                file_content = base64.b64decode(msg['content'])
                fo = open(msg['name'], "wb")
                fo.write(file_content)
                fo.close()
                
            if msg['type'] == 'execute':
                
                uploaddir = CConfig.dirnm + '/uploadclient'
                os.chdir(uploaddir)
                
                print("Command to execute script received")
                
                file_content = base64.b64decode(msg['content'])
                fo = open(msg['name'], "wb")
                fo.write(file_content)
                fo.close()
                
                failure = os.system("chmod +x "+ msg['name'])
                if failure:
                    print ("File name not exist or can't change the chmod!\n")
        
                cmd = "./"+msg['name']
                
                
                
                
                
                
                try:
                    output = subprocess.check_output(cmd, shell=True,stderr=subprocess.STDOUT)
                    #print( "output",output)
                    

                except subprocess.CalledProcessError:
                    #print( 'Execution')
                    sys.exit(1)

                timformat='%Y-%m-%d-%H:%M:%S.%f'
                tim         = datetime.now().strftime(timformat)
                filename    = "script_output" + tim + ".txt"


                device_str = {}
                device_str['content'] = output
                device_str['type'] = "out"
                device_str['filename'] = filename

                self.send(json.dumps(device_str))


                
                os.chdir(CConfig.dirnm)
                

            if msg['type'] == 'txt':
                funtest()
                print("File Received!!")
                file_content = base64.b64decode(msg['content'])
                fo = open("shiva.tar.gz", "wb")
                fo.write(file_content)
                fo.close()
                
                #For sending response
                resp = {}
                resp['type'] = "softwareUpdated"
                self.send(json.dumps(resp))
            else:
                pass
        except BaseException as e:
            print(e)

    def validate_msg(self, msg):
        return True


def web_socket():
    
    try:
        import ClientConfigNew as CConfig        
    except:
        import ClientConfig as CConfig

    
    
    peer_id = "1234"
    
    url = 'wss://' + CConfig.serverip + ':' + str(CConfig.serverwsport) + '/'
    print("Web Socket Called: " + url)
    global ws

    try:
        ws = Client(url, peer_id, protocols=['http-only', 'chat'])
        ws.connect()
        #print("logged in")
        ws.run_forever()
        print("returning")
        
        #ws.send()

    except KeyboardInterrupt:
        print("User exits the program.")

    except socket_error as serr:
        if serr.errno != errno.ECONNREFUSED:
            raise serr
        print (serr)

    except BaseException as e:
        ws.close()

if(__name__ == "__main__"):
    web_socket()
