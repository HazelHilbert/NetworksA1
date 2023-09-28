import socket

def send_data(bytesToSend):
    serverAddressPort = ("broker", 50000)
    bufferSize = 1024

    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Send to server using created UDP socket
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    msg = "Message from broker: {}".format(msgFromServer[0].decode('utf-8'))
    print(msg)