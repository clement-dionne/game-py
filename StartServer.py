import socket
import os
import time
import threading
import traceback

class TaskThread:

    def __init__(self, Fonction, Args = None):
        if Args != None:
            thread = threading.Thread(target = Fonction, args = Args)
        else:
            thread = threading.Thread(target = Fonction)
        thread.start()

def WaitForClient():
        while True:
            try:
                Server.listen()
                NewClientSocket, NewClientIP = Server.accept()
                AllClient[NewClientSocket] = NewClientIP
                TaskThread(ClientTask,(NewClientSocket, NewClientIP))
            except:
                Server.close()
                break

def ClientTask(ClientSocket:socket, ClientIP:int):
    print(str(ClientIP) + " join")
    while True:
        try:
            """
            if IsConnected(ClientSocket) == False:
                ClientSocket.close()
                del AllClient[ClientSocket]
                print(str(ClientIP) + " left")
                print(traceback.format_exc())
                break
            """
            ClientData = ClientSocket.recv(16384)
            ClientData = ClientData.decode('utf-8')
            TaskThread(BrodCastToAllClient(ClientData))
            ClientData = ""
        except:
            if IsConnected(ClientSocket) == False:
                ClientSocket.close()
                del AllClient[ClientSocket]
                print(str(ClientIP) + " left")
                print(traceback.format_exc())
                break

def BrodCastToAllClient(Data:str):
    for Client in AllClient:
        try :
            Client.send(bytes(Data, 'utf-8'))
        except:
            pass

def IsConnected(client):
    try:
        client.send(bytes("%&&", 'utf-8'))
        return True
    except Exception:
        return False
    return False

AllClient = dict()

# ServerIP = socket.gethostbyname(socket.gethostname())
ServerIP = "172.29.10.18"
print(ServerIP)
ServerPort = 7800
Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Server.bind((ServerIP, ServerPort))
TaskThread(WaitForClient)
quit()