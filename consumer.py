import socket
import struct # used to work with structured binary data i.e. the header


msgFromClient       = "Hello UDP broker"
bytesToSend         = str.encode(msgFromClient)
serverAddressPort   = ("broker", 50000)
bufferSize          = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

msgFromServer = UDPClientSocket.recvfrom(bufferSize)
msg = "Message from broker {}".format(msgFromServer[0])
print(msg)
