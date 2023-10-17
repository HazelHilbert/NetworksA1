import socket
from header import *

BROKER_ADDRESS = ("broker", 50000)

class UDM_Socket:
    def __init__(self, name):
        self.UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.bufferSize = 65536
        self.name = name

    def bind_to_address(self, addressPort):
        self.UDPSocket.bind(addressPort)
    
    def send_data_to(self, bytesToSend, addressPort):
        self.UDPSocket.sendto(bytesToSend, addressPort)
    
    def receive_data(self):
        return self.UDPSocket.recvfrom(self.bufferSize)[0]

    def receive_data_parsed(self):
        data = self.UDPSocket.recvfrom(self.bufferSize)
        
        packet_type = data[0][0]
        header = data[0][:get_header_length(packet_type)]
        payload = data[0][get_header_length(packet_type):]
        address = data[1]

        return (packet_type, header, payload, address)