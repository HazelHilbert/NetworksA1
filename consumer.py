import socket
from header import *


def send_data(bytesToSend):
    serverAddressPort = ("broker", 50000)
    bufferSize = 1024

    # Create a UDP socket at client side
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Send to server using created UDP socket
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    msg = "Message from broker {}".format(msgFromServer[0].decode('utf-8'))
    print(msg)


# allows producer to continusly announce streams or publish content
while True:
    action_input = input("Choose action (enter number):\n   1 --> Subscribe to Stream\n   2 --> Unsubscribe to Stream\n   3 --> Quit\n")

    # Subscribe to Stream
    if action_input == '1' or action_input == '2':
        # Ask for producer ID
        valid = False
        while not valid:
            id_input = input("Enter producer ID to subscribe to: ")
            if len(id_input) == 6:
                valid = True
                producer_ID = id_input.encode('utf-8')
            else:
                print("Invalid ID: enter 6 char string")

        valid = False
        while not valid:
            try:
                stream_input = input("Enter stream number or 'all' to subscribe to all streams: ")
                if stream_input == "all":
                    valid = True
                    if action_input == '1': 
                        packet_type = 3
                        payload = str.encode(str("Subscription request for all streams from: " + producer_ID.decode('utf-8')))
                    elif action_input == '2':
                        packet_type = 4
                        payload = str.encode(str("Unsubscribe request for all streams from: " + producer_ID.decode('utf-8')))
                    
                    header = make_header_3(packet_type, producer_ID)
                                
                elif 0 <= int(stream_input) <= 127:
                    valid = True
                    new_stream_number = int(stream_input)
                    if action_input == '1': 
                        packet_type = 5
                        payload = str.encode(str("Subscription request for stream: " + new_stream_number + " from: " + producer_ID.decode('utf-8')))
                    elif action_input == '2':
                        packet_type = 6
                        payload = str.encode(str("Unsubscribe request for stream: " + new_stream_number + " from: " + producer_ID.decode('utf-8')))
                    
                    header = make_header_1(packet_type, producer_ID, new_stream_number)
                else:
                    print("Invalid stream number: enter int [0, 127]")
            except:
                if valid == False:
                    print("Invalid stream number: enter int [0, 127]")

        send_data(header + payload)

    elif action_input == '3':
        break
    else:
        print("Invalid action")