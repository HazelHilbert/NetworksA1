import socket
from header import *

localIP     = "broker"
localPort   = 50000
bufferSize  = 1024

# header from producer 

msgFromServer       = "Received"
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
    packet_type = data[0]

    header = data[:get_header_length(data)]
    payload = data[get_header_length(data):]

    message_start = ''
    if packet_type == 1:
        message_start = "Received producer: "
    elif packet_type == 2:
        message_start = "Announced producer: "
    elif packet_type == 3 or packet_type == 4 or packet_type == 5 or packet_type == 6:
        message_start = "Consumer: "
    else:
        message_start = "ERROR "

    producertMsg = message_start + format(payload.decode('utf-8'))
    producerIP  = "IP Address:{}".format(address)
    
    print(producertMsg)
    print(producerIP)
        

    # Sending a reply
    UDPServerSocket.sendto(bytesToSend, address)
