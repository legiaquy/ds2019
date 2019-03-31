#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys,select,socket
# from socket import *


# In[ ]:


#----------------WE WRITE ALL CODES BY OURSELVES----------------

# CENTRAL SERVER'S HOST AND PORT
HOST = ""
PORT = 9999
SIZE = 2048
# THIS PEER'S NAME
my_name = ""    

#function for this peer to listen for other peers connections
def clisten(user_input):
    cport = int(user_input)
    host_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_peer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host_peer.bind((HOST,cport))
    print ('listening')
    host_peer.listen(10)
    inputs = [sys.stdin, host_peer] 
    my_clients = {} # List of other connected peers
    while True:
        try:
            inready,outready,exceptready = select.select(inputs, [], [])
            for s in inready:
                # Accept new incoming peer
                if s is host_peer:
                    try:
                        client_peer, client_address = s.accept()
                        inputs.append(client_peer)
                        my_clients[client_peer] = ''
                        client_peer.sendall(b"Welcome to " +str.encode(my_name)+ b"\nStart chatting...\n")
                    except:
                        print("Cannot accept new peer!")
                        return
                    
                # Outcoming msg to other peers
                elif s is sys.stdin:
                    resp = input("")
                    
                    # Broadcast outcoming msg to all connected peers
                    for c in inputs:
                        if c is not sys.stdin and c is not host_peer:
                            try:         
                                c.sendall(b"<HOST> " +str.encode(resp))
                            except:
                                print("Cannot broadcast outcoming msg!")
                                return
                    if resp == '\close':
                        print ('session ended')
                        return
                    
                # Incoming msg from another peer
                else:
                    msg = s.recv(SIZE).decode()
                    if "I'm" in msg:
                        my_clients[s] = msg.split()[1]
                        print(my_clients[s] + " is connected")

                        # Broadcast new peer to all connected peers
                        for c in inputs:
                            if c is not sys.stdin and c is not host_peer and c is not s:
                                try:
                                    #import ipdb; ipdb.set_trace() # debugging starts here
                                    c.sendall(str.encode(my_clients[s]) + b" is connected")
                                except:
                                    print("Cannot broadcast new peer!")
                                    return
                        continue

                    # Broadcast incoming msg to all connected peers
                    for c in inputs:
                        if c is not sys.stdin and c is not host_peer and c is not s:
                            try:

                                c.sendall(b"<"+str.encode(my_clients[s])+b"> "+str.encode(msg))
                            except:
                                print("Cannot broadcast incoming msg!")
                                return
                    print("<"+my_clients[s]+"> " +msg)
                    if msg == '\close':
                        s.close()
                        inputs.remove(s)
                        del my_clients[s]
        except:
            return
                

#function for client to connect to listening client                
def cconnect(data):
    cport = int(data)
    host_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_peer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        host_peer.connect((HOST,cport))
        host_peer.sendall(b"I'm " + str.encode(my_name))
    except:
        print ('Unable to connect to host')
    while True:
        inready,outready,exceptready = select.select([sys.stdin, host_peer], [], [])
        try:
            for s in inready:
                if s is host_peer:
                    msg = s.recv(SIZE).decode()
                    #import ipdb; ipdb.set_trace() # debugging starts here
                    if msg == '<HOST> \close':
                        print ('session ended')
                        host_peer.close()
                        return
                    print(msg)
                else:
                    resp = input("")
                    host_peer.send(str.encode(resp)) 
                    if resp == '\close':
                        print ('session ended')
                        host_peer.close()
                        return
        except:
            print("Unable to chat to host!")

def main():
    global my_name
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Unable to connect to server")
        return
    print("Connected to server")

    while True:
        try:
            # Incoming msg from server
            msg = server.recv(SIZE).decode()
            
            # Receive my name
            if "Welcome" in msg:
                my_name += msg.split()[1]
                
            # Receive permission and port to start listening 
            if "Your Port:" in msg:
                clisten(msg.split()[2])
                server.sendall(b"\close")
                continue
            
            # Receive permission and host's port to start connecting
            if "Connecting To:" in msg:
                cconnect(msg.split()[2])
                server.sendall(b"\close")
                continue
                
            # Outcoming msg to server
            user_input = input(msg)  
            if user_input == "\quit":
                server.sendall(b"\quit")
                server.close()
                return
            server.send(str.encode(user_input))                
        except:
            print("Cannot receving msg from server!")
            server.sendall(b"\quit")
            server.close()
            return

if __name__ == "__main__":
    sys.exit(main())


# In[ ]:




