import os 
from header import *
from udm_socket import *

# Ask for producer ID
valid = False
while not valid:
    id_input = input("Enter producer ID: ")
    if len(id_input) == 6:
        valid = True
        producer_ID = id_input.encode('utf-8')
    else:
        print("Invalid ID: enter 6 char string")

# Create a datagram socket
producer_socket = UDM_Socket("producer")

stream_list = []
# allows producer to continusly announce streams or publish content
while True:
    action_input = input("Choose action (enter number):\n   1 --> Announce Stream\n   2 --> Publish Content\n   3 --> Quit\n")

    # Anounce stream
    if action_input == '1':
        packet_type = 1
        valid = False
        while not valid:
            try:
                stream_input = int(input("Enter stream number: "))
                if 0 <= stream_input <= 127:
                    valid = True
                    stream_list.append(stream_input)
                    new_stream_number = stream_input
                else:
                    print("Invalid stream number: enter int [0, 127]")
            except:
                if valid == False:
                    print("Invalid stream number: enter int [0, 127]")

        # construct header
        header = make_header_1(packet_type, producer_ID, new_stream_number)

        # data payload
        payload = str.encode(str(producer_ID.decode('utf-8')) + ", adding stream: " + str(new_stream_number))
        
        # send to broker
        producer_socket.send_data_to(header + payload, BROKER_ADDRESS)

        # get response
        print("Message from broker: " + producer_socket.receive_data().decode('utf-8'))

    # Publish content
    elif action_input == '2':
        packet_type = 2
        
        valid = False
        while not valid:
            try:
                stream_input = int(input("Enter stream number: "))
                if 0 <= stream_input <= 127:
                    if stream_list.__contains__(stream_input):
                        valid = True
                        stream_number = stream_input
                    else:
                        print("Please announce stream before publishing content")
                        break
                else:
                    print("Invalid stream number: enter int [0, 127]")
            except:
                if valid == False:
                    print("Invalid stream number: enter int [0, 127]")

        if valid == True:
            valid = False
            while not valid:
                try:
                    folder_input = input("Enter folder to broadcast: ")
                    list_of_frames = os.listdir(os.getcwd() + '/' + folder_input)
                    valid = True
                except:
                    if (valid == False):
                        print("Could not find folder")

            frame = 1
            for frame_name in list_of_frames:
                payload_size = int(os.stat(os.getcwd() + '/' + folder_input + '/' + frame_name).st_size)
                
                # construct header
                header = make_header_2(packet_type, producer_ID, stream_number, frame, payload_size)

                # data payload
                payload = str.encode(str(producer_ID.decode('utf-8')) + ", stream: " + str(stream_number) + ", frame: " + str(frame) + ", payload size: " + str(payload_size))
                
                # send to broker
                producer_socket.send_data_to(header + payload, BROKER_ADDRESS)
                
                # get response
                print("Message from broker: " + producer_socket.receive_data().decode('utf-8'))

                frame += 1

    elif action_input == '3':
        break
    else:
        print("Invalid action")