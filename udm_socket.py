import socket

BROKER_ADDRESS = ("broker", 50000)

class UDM_Socket:
    def __init__(self, name):
        self.UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.bufferSize = 1024
        self.name = name

    def bind_to_address(self, addressPort):
        self.UDPSocket.bind(addressPort)
    
    def send_data_to(self, bytesToSend, addressPort):
        self.UDPSocket.sendto(bytesToSend, addressPort)
        
    def receive_data(self):
        return self.UDPSocket.recvfrom(self.bufferSize)