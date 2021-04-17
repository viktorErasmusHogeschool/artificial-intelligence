import socket
import pickle

class Network:

    def __init__(self):
        # At the client-side, a socket is created in exactly the same way as at the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "172.104.134.93"
        self.port = 5555
        self.addr = (self.host, self.port)
        # Now the difference exists at the client-side in a way that instead of listening to the socket,
        # we need to connect to the one that is already opened by the server. To do so, we use the connect method:
        self.initial_sample = self.connect()

    def connect(self):
        # At the server-side, the accept method will open a connection with the previously connected client
        self.client.connect(self.addr)
        return pickle.loads(self.client.recv(2048))

    def send(self, data):
        try:
            # Send data to the server
            # print("Sending: {}".format(self.client.send(str.encode(data))))
            self.client.send(str.encode(data))
            # Retrieve data on the server
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)
