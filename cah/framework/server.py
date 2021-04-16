import socket
from _thread import *
from .deck import Deck

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = ''
port = 5555

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

# maximum number of connections that will be available in
# the connection queue before calling the accept method
s.listen(2)
print("Waiting for a connection")


# Define card deck common to all games
deck = Deck()
# Keep track of number of players
number_of_players = 0


def threaded_client(conn):
    global deck, number_of_players
    while True:
        try:
            # The decoded data is a list of played cards
            data = conn.recv(2048).decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
            else:
                #reply =
                print("Received: {}".format(reply))

            conn.sendall(str.encode(reply))
        except:
            break


while True:
    # this function blocks the server until an incoming connection appears,
    # and returns the socket object associated with it and the address of
    # the connected host. The address is an array of IP address and port number.
    conn, addr = s.accept()
    number_of_players += 1
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn,))

currentId = "0"
pos = ["0:50,50", "1:100,100"]


def threaded_client(conn):
    global currentId, pos
    conn.send(str.encode(currentId))
    currentId = "1"
    reply = ''
    while True:
        try:
            # read & decode incoming data from the client-side
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                print("Received: " + reply)
                arr = reply.split(":")
                id = int(arr[0])
                # Update position of Player[id]
                pos[id] = reply

                if id == 0: nid = 1
                if id == 1: nid = 0

                reply = pos[nid][:]
                # Send out position of other player
                print("Sending: " + reply)

            # Send the data to the client side
            conn.sendall(str.encode(reply))
        except:
            break

    print("Connection Closed")
    conn.close()


while True:
    # this function blocks the server until an incoming connection appears,
    # and returns the socket object associated with it and the address of
    # the connected host. The address is an array of IP address and port number.
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn,))
