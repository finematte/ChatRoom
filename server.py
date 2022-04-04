import socket
import threading
import json

PORT = 10000
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

server.listen()

clients = []
nicknames = []


def broadcast(message):
    for client in clients:
        client.send(message)


def wake_up(exception):
    for client in clients:
        if client is not exception:
            client.send('!WAKEUP'.encode(FORMAT))
            client.send(f'You have been woken up by {nicknames[clients.index(exception)]}!'.encode(FORMAT))


def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if '!USERNAMES' in message.decode(FORMAT):
                data = json.dumps({'!USERNAMES': nicknames})
                client.send(data.encode(FORMAT))
            elif '!WAKEUP' in message.decode(FORMAT):
                wake_up(client)
            elif '!DISCONNECT' in message.decode(FORMAT):
                broadcast(f'User {nicknames[clients.index(client)]} has left the chat!'.encode(FORMAT))
                print(f'{nicknames[clients.index(client)]} has left the chat!')
                client.close()
            else:
                broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break


def start():
    print(f"[LISTENING] Server is listening on {SERVER}\n")

    while True:
        client, addr = server.accept()

        nickname = client.recv(1024).decode(FORMAT)
        if nickname in nicknames:
            client.send('This nickname is already taken! Choose another one!'.encode(FORMAT))
        else:
            client.send('OK'.encode(FORMAT))
            nicknames.append(nickname)
            clients.append(client)
            print(f'{nickname} joined the chat!')
            broadcast(f'{nickname} joined the chat!'.encode(FORMAT))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()
    #  print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] Server is starting...")
start()
