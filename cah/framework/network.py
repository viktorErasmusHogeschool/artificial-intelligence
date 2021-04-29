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
        self.initiate = self.connect()

    def connect(self):
        # At the server-side, the accept method will open a connection with the previously connected client
        self.client.connect(self.addr)
        return pickle.loads(self.client.recv(4096))

    def send(self, data):
        # Send data to the server
        self.client.send(pickle.dumps(data))
        return pickle.loads(self.client.recv(4096))

    def receive(self):
        # Retrieve data on the server
        pass

