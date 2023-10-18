import os
import random
import time 
from header import *
from udm_socket import *
import zlib

# Ask for producer ID
valid = False
while not valid:
    id_input = input("Enter producer ID: ")
    if len(id_input) == 6:
        try:
            producer_ID = bytes.fromhex(id_input)
            valid = True
        except:
            print("Invalid ID: enter 6 char string representing a 3 byte hexadecimal number")
            continue
    else:
        print("Invalid ID: enter 6 char string representing a 3 byte hexadecimal number")

# Create a datagram socket
producer_socket = UDM_Socket("producer")
producer_socket.set_timeout(0.1)

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
        header = make_header(packet_type, producer_ID, new_stream_number)

        # data payload
        payload = str.encode(str(producer_ID.hex().upper()) + ", adding stream: " + str(new_stream_number))
        
        # send to broker
        producer_socket.send_data_to(header + payload, BROKER_ADDRESS)

        # get response
        print("Message from broker: " + producer_socket.receive_data().decode('utf-8'))

    # Publish content
    elif action_input == '2':
        packet_type_frame = 2
        packet_type_audio = 8
        
        # Get input for strem number
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
            # get input for frames
            valid = False
            while not valid:
                try:
                    folder_input = input("Enter folder with frames to broadcast: ")
                    list_of_frames = os.listdir(os.getcwd() + '/' + folder_input)
                    valid = True
                except:
                    if (valid == False):
                        print("Could not find folder")
            
            # get input for audio
            valid = False
            while not valid:
                try:
                    audio_input = input("Enter audio to broadcast (or none): ")
                    with open(audio_input, 'rb') as audio_file:
                        audio_encode = audio_file.read()
                    audio_chunk_size = len(audio_encode)//len(list_of_frames)
                    has_audio = True
                    valid = True
                except:
                    if audio_input == "none":
                        has_audio = False
                        valid = True
                    elif (valid == False):
                        print("Could not find audio file")

            # broadcast frames/audio
            for i in range(len(list_of_frames)):
                # get frame payload
                current_frame_path = os.getcwd() + '/' + folder_input + '/' + list_of_frames[i]
                with open(current_frame_path, 'rb') as file:
                    payload_frame = file.read()

                # calculate CRC-32 value
                crc_value_frame = zlib.crc32(payload_frame) & 0xFFFFFFFF
        
                # construct frame header
                header_frame = make_header(packet_type_frame, producer_ID, stream_number, i+1, crc_value_frame)
                
                response_received = False
                tries = 0
                while not response_received and tries < 3:
                    tries += 1
                    # ADDING FILE CORRUPTION TO TEST ERROR PREDICTION
                    payload_frame_corrupted = payload_frame
                    if random.random() < 0.1:
                        payload_frame_corrupted += b'01'

                    # send to broker
                    producer_socket.send_data_to(header_frame + payload_frame_corrupted, BROKER_ADDRESS)
                    
                    # try to recive response
                    response_received = False
                    try:
                        data = producer_socket.receive_data_parsed()
                        packet_type = data[0]
                        payload = data[2]
                        if packet_type == 7:
                            print("Acknowledgment from broker: " + payload.decode('utf-8'))
                            response_received = True
                        else:
                            print("Negatice response, retransmitting frame", i + 1)
                    except:
                        print("No response in time, retransmitting frame", i + 1)
                    
                # send audio
                if has_audio:
                    payload_audio = audio_encode[i * audio_chunk_size:(i + 1) * audio_chunk_size]
                    # calculate CRC-32 value
                    crc_value_audio = zlib.crc32(payload_audio) & 0xFFFFFFFF
                    header_audio = make_header(packet_type_audio, producer_ID, stream_number, i+1, crc_value_audio)
                    producer_socket.send_data_to(header_audio + payload_audio, BROKER_ADDRESS)
                    # NEED TO CHANGE THIS
                    print("Message from broker: " + producer_socket.receive_data().decode('utf-8'))

    elif action_input == '3':
        break
    else:
        print("Invalid action")