import select, sys, zlib
from header import *
from udm_socket import *
from user_input import *

# Create a datagram socket
consumer_socket = UDM_Socket("consumer")

input_sockets = [sys.stdin, consumer_socket.UDPSocket]
output_sockets = []

menu = "Choose action (enter number):\n   1 --> Subscribe to Stream\n   2 --> Unsubscribe to Stream\n   3 --> Quit\n"
print(menu)

# allows producer to continusly announce streams or publish content
quit = False
while not quit:
    readable, writable, _ = select.select(input_sockets, output_sockets, [])

    for sock in readable:
        if sock is sys.stdin:
            action_input = input()

            # Subscribe to Stream
            if action_input == '1' or action_input == '2':
                # get producer ID to sub to
                producer_ID = input_producer_id_sub()
                producer_ID_string = str(producer_ID.hex().upper())

                valid = False
                while not valid:
                    try:
                        stream_input = input("Enter stream number or 'all' to subscribe/unsubscribe to all streams: ")
                        if stream_input == "all":
                            valid = True
                            if action_input == '1': 
                                packet_type = 3
                                payload = str.encode("Subscription request for all streams from: " + producer_ID_string)
                            elif action_input == '2':
                                packet_type = 4
                                payload = str.encode("Unsubscribe request for all streams from: " + producer_ID_string)
                            
                            header = make_header(packet_type, producer_ID)
                            consumer_socket.send_data_to(header + payload, BROKER_ADDRESS)
                            
                            # get response
                            print("Message from broker: " + consumer_socket.receive_data().decode('utf-8'))

                        elif 0 <= int(stream_input) <= 127:
                            valid = True
                            new_stream_number = int(stream_input)
                            if action_input == '1': 
                                packet_type = 5
                                payload = str.encode("Subscription request for stream: " + str(new_stream_number) + " from: " + producer_ID_string)
                            elif action_input == '2':
                                packet_type = 6
                                payload = str.encode("Unsubscribe request for stream: " + str(new_stream_number) + " from: " + producer_ID_string)
                            
                            header = make_header(packet_type, producer_ID, new_stream_number)
                            consumer_socket.send_data_to(header + payload, BROKER_ADDRESS)
                            
                            # get response
                            print("Message from broker: " + consumer_socket.receive_data().decode('utf-8'))
                    
                        else:
                            print("Invalid stream number: enter int [0, 127]")
                    except:
                        if valid == False:
                            print("Invalid stream number: enter int [0, 127]")

            elif action_input == '3':
                quit = True
                break
            else:
                print("Invalid action")
            
            print(menu)
        
        elif sock is consumer_socket.UDPSocket:
            try:
                data = consumer_socket.receive_data_parsed()
                packet_type = data[0]
                header = data[1]
                payload = data[2]
                address = data[3]
                producer_id = get_producer_id(header)
                producer_id_bytes = get_producer_id_bytes(header)

                if packet_type == 2:
                    discription = " frame: "
                else:
                    discription = " audio chunk: "

                # calculate the CRC-32 checksum for the received frame
                received_crc = int(zlib.crc32(payload))
                expected_crc = int(get_crc_value(header))
                # Verify the CRC checksum
                if received_crc != expected_crc:
                    msgFromServer = "CRC-32 checksum did not match"
                    message_start = "ERROR: Received corrupted from broker: "
                else:
                    msgFromServer = "Recived" + discription + str(get_frame_number(header))
                    message_start = "Received from broker: producer: "
                
                # print which stream/audio chunck recived
                print(message_start + str(producer_id) + "; stream: " + str(get_stream_number(header)) + ";" + discription + str(get_frame_number(header)))
                
                # send reply if not corupted
                if received_crc == expected_crc:
                    stream_number = get_stream_number(header)
                    frame_number = get_frame_number(header)
                    header = make_header(7, producer_id_bytes, int(stream_number), int(frame_number))
                    payload = str.encode(msgFromServer)        
                    consumer_socket.send_data_to(header + payload, address)
            except:
                continue