from header import *
from udm_socket import *

# Create a datagram socket
consumer_socket = UDM_Socket("consumer")

# allows producer to continusly announce streams or publish content
while True:
    action_input = input("Choose action (enter number):\n   1 --> Subscribe to Stream\n   2 --> Unsubscribe to Stream\n   3 --> Quit\n")

    # Subscribe to Stream
    if action_input == '1' or action_input == '2':
        # Ask for producer ID
        valid = False
        while not valid:
            id_input = input("Enter producer ID to subscribe/unsubscribe to: ")
            if len(id_input) == 6:
                valid = True
                producer_ID = id_input.encode('utf-8')
            else:
                print("Invalid ID: enter 6 char string")

        valid = False
        while not valid:
            try:
                stream_input = input("Enter stream number or 'all' to subscribe/unsubscribe to all streams: ")
                if stream_input == "all":
                    valid = True
                    if action_input == '1': 
                        packet_type = 3
                        payload = str.encode(str("Subscription request for all streams from: " + producer_ID.decode('utf-8')))
                    elif action_input == '2':
                        packet_type = 4
                        payload = str.encode(str("Unsubscribe request for all streams from: " + producer_ID.decode('utf-8')))
                    
                    header = make_header_3(packet_type, producer_ID)
                    consumer_socket.send_data_to(header + payload, BROKER_ADDRESS)
                    
                    # get response
                    print("Message from broker: " + consumer_socket.receive_data().decode('utf-8'))

                elif 0 <= int(stream_input) <= 127:
                    valid = True
                    new_stream_number = int(stream_input)
                    if action_input == '1': 
                        packet_type = 5
                        payload = str.encode(str("Subscription request for stream: " + str(new_stream_number) + " from: " + producer_ID.decode('utf-8')))
                    elif action_input == '2':
                        packet_type = 6
                        payload = str.encode(str("Unsubscribe request for stream: " + str(new_stream_number) + " from: " + producer_ID.decode('utf-8')))
                    
                    header = make_header_1(packet_type, producer_ID, new_stream_number)
                    consumer_socket.send_data_to(header + payload, BROKER_ADDRESS)
                    
                    # get response
                    print("Message from broker: " + consumer_socket.receive_data().decode('utf-8'))
            
                else:
                    print("Invalid stream number: enter int [0, 127]")
            except:
                if valid == False:
                    print("Invalid stream number: enter int [0, 127]")

    elif action_input == '3':
        while True:
            data = consumer_socket.receive_data_parsed()
            packet_type = data[0]
            header = data[1]
            payload = data[2]
            address = data[3]
        
            msgFromServer = "Received"
            message_start = "Received from producer: "
            
            print(message_start + format(payload.decode('utf-8')))

            # send a reply
            consumer_socket.send_data_to(str.encode(msgFromServer), address)

            
    else:
        print("Invalid action")
            