#!/usr/bin/env python
# coding: utf-8

# In[1]:


import socket,select,sys
import sqlite3 as sql
import pandas as pd
from hashlib import sha1 as sha
from threading import Thread


# In[ ]:


# --------OUR MODIFICATION--------------------- 

#-----INITIALIZE VARIABLES-----       
HOST = ""
PORT = 9999
SIZE = 1024
DATABASE = "users.db"


#-----INITIALIZE DATABASE-----
db_conn = sql.connect(DATABASE)
cursor = db_conn.cursor()
cursor.execute("DROP TABLE users")
cursor.execute('''CREATE TABLE users
            (name text, password text)''')
db_conn.commit()
db_conn.close()

# function to see database
def see_db(db):
    db_conn = sql.connect(db)
    df = pd.read_sql_query("SELECT * FROM users", db_conn)
    return df

def cclose(client,c_port,c_name):
    if client in c_port.keys():
        del c_port[client]
    if client in c_name.keys():
        del c_name[client]
    client.close()

# function to create account, encrypt pwd and save to database
def set_account(client,name,raw_pwd, db, c_port):
    db_conn = sql.connect(db)
    cursor = db_conn.cursor()
    verify = "SELECT name FROM users WHERE name=?"
    cursor.execute(verify, (name,))
    exists = cursor.fetchone()
    if not exists:
        raw_pwd = sha(raw_pwd.encode("utf-8")).hexdigest()
        create = "INSERT INTO users VALUES (?,?)"
        cursor.execute(create, (name,raw_pwd,))
        db_conn.commit()
        db_conn.close()
        return 1
    else:
        client.sendall(b"\nUsername is already taken. Type 'Y' to set new username")

# function to validate user's account in the database
def check(name,raw_pwd, db):
    raw_pwd = sha(raw_pwd.encode("utf-8")).hexdigest()
    db_conn= sql.connect(db)
    cursor= db_conn.cursor()
    verify = "SELECT * FROM users WHERE name=? AND password=?"
    cursor.execute(verify, (name,raw_pwd,))
    valid = cursor.fetchone()
    if valid:
        return 1
    else:
        return 0

# function to login in the chat system
def login(client,name,raw_pwd,db,c_name):
    if not check(name,raw_pwd,db):
        client.sendall(b"\nIncorrect username or password! Try again")
        return 0
    if name in c_name.values():
        client.sendall(b"\nAlready connected")
        return 0
    else:
        return 1

# function to respond user's request to bind to a port   
def listen(client,c_name,c_port):
    msg = b"\nListening Port: "
    client.sendall(msg)
    port = client.recv(SIZE).decode()
    c_port[c_name[client]] = port
    client.sendall(b"\nYour Port: " + str.encode(port))
    if client.recv(SIZE).decode() == '\close':
        del c_port[c_name[client]]
        client.sendall(b"\nType your request or type \help for help\n")
        return

        
# function to respond user's request to connect to another peer
def connect(client,c_port):
    client.sendall(b"\nHostname: ")
    name = client.recv(SIZE).decode()
    if name in c_port:
        client.sendall(b"Connecting To: " + str.encode(c_port[name]) + b" " + str.encode(name))
        if client.recv(SIZE).decode() == '\close':
            client.sendall(b"\nType your request or type \help for help\n")
            return
    else:
        client.sendall(b"\nYour friend not listening\n")
    
# function to handle requests from users                    
def start(client,db,c_port,c_name):
    while True:
        try:
            data = client.recv(SIZE).decode()
            if data == 'y' or data == 'Y':    #requests new username and password if new user
                client.sendall(b"\nSet new username & password\nusername: ")
                name = client.recv(SIZE).decode()
                client.sendall(b"\npassword: ")
                pwd = client.recv(SIZE).decode()
                if set_account(client,name,pwd,db,c_port):
                    c_name[client] = name
                    # CONNECT HERE
                    print("\n"+c_name[client]+" is connected")
                    client.sendall(b"\nWelcome "+str.encode(name)+b"\nType your request or type \help for help\n") 

            elif data == 'n' or data == 'N':   #if existing user, it verifies the username and password
                for x in range(0, 3):          #provides three attempts for user to login
                    client.sendall(b"\nType your username and password\nusername: ")
                    name = client.recv(SIZE)
                    name = name.decode()
                    client.sendall(b"\npassword: ")
                    pwd = client.recv(SIZE).decode()
                    if login(client,name,pwd,db,c_name):
                        c_name[client] = name
                        # CONNECT HERE
                        print("\n"+c_name[client]+" is connected")
                        client.sendall(b"\nWelcome " +str.encode(name)+b'\nType your request or type \help for help\n')
                        break
                    if x == 2:
                        client.sendall(b'\nYou have exceeded the no. of retries')
                        cclose(client, c_port, c_name)
            elif data == '\help': #if help command is given
                usage(client)    

            elif data == '\list': #sendall list of connected clients to user
                client.sendall(b'\n\list: ' +str.encode(str(c_port.keys()))+b'\n')

            elif data == '\listen': #listen to a port
                listen(client,c_name,c_port)

            elif data == '\connect': #sendalls listening port of client
                connect(client,c_port) 

            elif data == '\see_db':
                client.sendall(b"OK")
                print(see_db(db))
            elif data == '\quit': #disconnect client if requested
                print("\n"+c_name[client]+" is quit")
                cclose(client, c_port, c_name)
            else:
                client.sendall(b"\nWrong syntax!")

        except:
            print ("\n" + c_name[client] + " is quit")
            cclose(client, c_port, c_name)
# --------OUR MODIFICATION--------------------- 


# function for help command
def usage(client):
    msg= '''
    Command List:
    \list - to request list of listening peers
    \listen - to listen to a port for being connected
    \connect - to connect to a listening peer
    \quit –  to indicate that you are no longer connected to the chat service\n\n'''
    client.sendall(str.encode(msg))

def main():
    #-----INITIALIZE SOCKET-----
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #-----BINDING SOCKET TO LOCALHOST AND PORT-----
    server.bind((HOST, PORT))
    server.listen(10)
    
    # --------OUR MODIFICATION--------------------- 
    c_port = {} # List of peers' listening port
    c_name = {} # List of peers' name
    
    print ("\nChat server is now running on port " + str(PORT))
    while True:
        client, address = server.accept()
        client.sendall(b"\nAre you a new user? Type Y or N: ")
        Thread(target=start, args=(client, DATABASE, c_port, c_name)).start()
        print("Start thread")
    # --------OUR MODIFICATION--------------------- 

if __name__ == "__main__":
    main()
#     print(see_db(DATABASE))


# In[ ]:




