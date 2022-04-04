import socket
import threading
import time
import json
import os
import PySimpleGUI as sg
from boombox import BoomBox

PORT = 10000
FORMAT = 'utf-8'
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)


def initialize_connection():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    return client


def connect(username, conn):
    client = conn
    client.connect(ADDR)
    client.send(username.encode(FORMAT))

    message = client.recv(1024).decode(FORMAT)
    if message == 'OK':
        return conn
    else:
        print(message)
        client.close()
        finalClient = initialize_connection()
        return finalClient


def receive(conn):
    client = conn

    while True:
        try:
            message = client.recv(1024).decode(FORMAT)
            if "!USERNAMES" in message:
                data = json.loads(message)
                print(f"Active users: {', '.join(map(str, data['!USERNAMES']))}")
            elif "!WAKEUP" in message:
                path = os.getcwd()
                boombox = BoomBox(path + "\\note.wav")
                boombox.play()
            elif message == f"User {user} has left the chat!":
                pass
            elif message == '':
                pass
            else:
                print(message)
        except:
            client.close()
            break


sg.theme('GreenTan')

center_login = [[sg.Text('Login', size=(5, 1)), sg.InputText(size=(20, 1), key='-USER-'),
                 sg.Button('Connect', button_color=(sg.YELLOWS[0], sg.BLUES[0]), bind_return_key=False),
                 sg.Button('Disconnect', button_color=(sg.YELLOWS[0], sg.BLUES[0]), bind_return_key=False)]]

layout = [[sg.Column(center_login, vertical_alignment='center', justification='center', key='-C-'), sg.Button('Exit', button_color=(sg.YELLOWS[0], sg.BLUES[0]), bind_return_key=False)],
          [sg.Output(size=(67, 20), font='Helvetica 11')],
          [sg.Multiline(size=(35, 2), enter_submits=True, key='-QUERY-', do_not_clear=False),
           sg.Button('Send', button_color=(sg.YELLOWS[0], sg.BLUES[0]), bind_return_key=True),
           sg.Button('Users', button_color=(sg.YELLOWS[0], sg.BLUES[0]), bind_return_key=False),
           sg.Button('Wake up!', button_color=(sg.YELLOWS[0], sg.BLUES[0]), bind_return_key=False)]]

window = sg.Window('Chat window', layout, font=('Helvetica', ' 13'), default_button_element_size=(8, 2),
                   use_default_focus=False, finalize=True)
window['-C-'].expand(True, True, True)

user = ''
connected = False

while True:
    event, value = window.read()
    connection = initialize_connection()

    if event in (sg.WIN_CLOSED, 'EXIT'):
        break
    if event == 'Exit':
        try:
            if connected == True:
                client.send("!DISCONNECT".encode(FORMAT))
                print('You have been disconnected!')
                client.close()
                break
            else:
                break
        except:
            pass
    if event == 'Connect':
        query = value['-USER-'].strip()
        if not query:
            print("Nickname can not be empty!")
        else:
            try:
                client.send("!DISCONNECT".encode(FORMAT))
                time.sleep(0.5)
                client.close()
            except:
                pass
            try:
                client = connect(query, connection)
                user = query
                connected = True
                receive_thread = threading.Thread(target=receive, args=(client,))
                receive_thread.start()
            except:
                pass
    if event == 'Disconnect':
        try:
            client.send("!DISCONNECT".encode(FORMAT))
            print('You have been disconnected!')
            client.close()
            connected = False
        except:
            print("You are not connected!")
    if event == 'Send':
        query = value['-QUERY-'].rstrip()
        try:
            if not connected:
                pass
            elif not query:
                print("Message can not be empty!")
            else:
                client.send(f'{user}: {query}'.encode(FORMAT))
        except:
            print("You are not connected!")
    if event == 'Wake up!':
        try:
            client.send('!WAKEUP'.encode(FORMAT))
        except:
            pass
    if event == 'Users':
        try:
            client.send('!USERNAMES'.encode(FORMAT))
        except:
            pass

window.close()
