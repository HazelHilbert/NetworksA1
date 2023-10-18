import os, random, zlib
from header import *
from udm_socket import *
from user_input import *

# Ask for producer ID
producer_ID = input_producer_id()

# Create a datagram socket
producer_socket = UDM_Socket("producer")
producer_socket.set_timeout(0.1)

# sends data with flow control
def send_data(packet_type, producer_ID, stream_number, frame_number, payload):
    # calculate CRC-32 value
    crc_value = zlib.crc32(payload) & 0xFFFFFFFF

    # construct header
    header = make_header(packet_type, producer_ID, stream_number, frame_number, crc_value)
    
    response_received = False
    tries = 0
    while not response_received and tries < 3:
        tries += 1
        # ADDING FILE CORRUPTION TO TEST ERROR PREDICTION
        payload_corrupted = payload
        if random.random() < 0.1:
            payload_corrupted += b'01'

        # send to broker
        producer_socket.send_data_to(header + payload_corrupted, BROKER_ADDRESS)
        
        # try to recive response
        try:
            response_data = producer_socket.receive_data_parsed()
            response_packet_type = response_data[0]
            response_payload = response_data[2]
            if response_packet_type == 7:
                print("Acknowledgment from broker: " + response_payload.decode('utf-8'))
                response_received = True
            else:
                print("Negatice response, retransmitting frame", frame_number)
        except:
            print("No response in time, retransmitting frame", frame_number)
  
stream_list = []
# allows producer to continusly announce streams or publish content
while True:
    action_input = input("Choose action (enter number):\n   1 --> Announce Stream\n   2 --> Publish Content\n   3 --> Quit\n")

    # Anounce stream
    if action_input == '1':
        packet_type = 1

        # get stream input
        new_stream_number = input_new_stream(stream_list)
        
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
        # Get input for stream number
        stream_number = input_stream(stream_list)

        if stream_number >= 0:
            # get input for frames
            result_input_frames = input_frames()
            folder_input = result_input_frames[0]
            list_of_frames = result_input_frames[1]
            
            # get input for audio
            result_input_audio = input_audio(list_of_frames)
            has_audio = result_input_audio[0]
            
            packet_type_frame = 2
            packet_type_audio = 8
            # broadcast frames/audio
            for i in range(len(list_of_frames)):
                # get frame payload
                current_frame_path = os.getcwd() + '/' + folder_input + '/' + list_of_frames[i]
                with open(current_frame_path, 'rb') as file:
                    payload_frame = file.read()

                # send frame data
                send_data(packet_type_frame, producer_ID, stream_number, i+1, payload_frame)

                # send audio data
                if has_audio:
                    audio_encode = result_input_audio[1]
                    audio_chunk_size = result_input_audio[2]
                    payload_audio = audio_encode[i * audio_chunk_size:(i + 1) * audio_chunk_size]
                    send_data(packet_type_audio, producer_ID, stream_number, i+1, payload_audio)

    elif action_input == '3':
        break
    else:
        print("Invalid action")