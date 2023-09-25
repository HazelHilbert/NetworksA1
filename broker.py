import socket
from header import *

localIP     = "broker"
localPort   = 50000
bufferSize  = 1024

# header from producer 

msgFromServer       = "Hello UDP Producer"
bytesToSend         = str.encode(msgFromServer)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP broker up and listening")

# Listen for incoming datagrams
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    data = bytesAddressPair[0]
    address = bytesAddressPair[1]

    header = data[:get_header_length(data)]
    payload = data[get_header_length(data):]

    if data[0] <= 2:
        producertMsg = "Message from Producer:{}".format(payload)
        producerIP  = "Producer IP Address:{}".format(address)
    
        print(producertMsg)
        print(producerIP)

    # Sending a reply
    UDPServerSocket.sendto(bytesToSend, address)
