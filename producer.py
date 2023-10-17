import os 
from header import *
from udm_socket import *
import crcmod.predefined

# create a CRC-16 generator
crc16 = crcmod.predefined.Crc('crc-16')

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
        payload = str.encode(str(producer_ID.hex().upper()) + ", adding stream: " + str(new_stream_number))
        
        # send to broker
        producer_socket.send_data_to(header + payload, BROKER_ADDRESS)

        # get response
        print("Message from broker: " + producer_socket.receive_data().decode('utf-8'))

    # Publish content
    elif action_input == '2':
        packet_type_frame = 2
        packet_type_audio = 8
        
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
                    folder_input = input("Enter folder with frames to broadcast: ")
                    list_of_frames = os.listdir(os.getcwd() + '/' + folder_input)
                    valid = True
                except:
                    if (valid == False):
                        print("Could not find folder")

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

            frame = 1
            for i in range(len(list_of_frames)):
                # get frame payload
                current_frame_path = os.getcwd() + '/' + folder_input + '/' + list_of_frames[i]
                with open(current_frame_path, 'rb') as file:
                    payload_frame = file.read()

                # calculate CRC-16 value of 2 bytes
                crc_value_frame = crc16(payload_frame).to_bytes(2, byteorder='big')

                # construct frame header
                header_frame = make_header_2(packet_type_frame, producer_ID, stream_number, frame, crc_value_frame)

                # send to broker
                producer_socket.send_data_to(header_frame + payload_frame, BROKER_ADDRESS)
                
                # get response
                print("Message from broker: " + producer_socket.receive_data().decode('utf-8'))
                
                # send audio
                if has_audio:
                    payload_audio = audio_encode[i * audio_chunk_size:(i + 1) * audio_chunk_size]
                    # calculate CRC-16 value of 2 bytes
                    crc_value_audio = crc16(payload_audio).to_bytes(2, byteorder='big')
                    header_audio = make_header_2(packet_type_audio, producer_ID, stream_number, frame, crc_value_audio)
                    producer_socket.send_data_to(header_audio + payload_audio, BROKER_ADDRESS)
                    print("Message from broker: " + producer_socket.receive_data().decode('utf-8'))

                frame += 1

    elif action_input == '3':
        break
    else:
        print("Invalid action")