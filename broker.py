import socket, struct

localIP     = "broker"
localPort   = 50000
bufferSize  = 1024

# header from producer 
header_format_1 = 'b 6s b'
header_format_2 = 'b 6s b i i'

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

    packet_type = data[0]
    if packet_type == 1:
        header_format = header_format_1
    elif packet_type == 2:
        header_format = header_format_2

    header = data[:struct.calcsize(header_format)]
    payload = data[struct.calcsize(header_format):]

    if packet_type <= 2:
        producertMsg = "Message from Producer:{}".format(payload)
        producerIP  = "Producer IP Address:{}".format(address)
    
        print(producertMsg)
        print(producerIP)

    # Sending a reply
    UDPServerSocket.sendto(bytesToSend, address)
