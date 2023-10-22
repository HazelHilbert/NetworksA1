import os
from header import *
from udm_socket import *
from user_input import *

# Ask for producer ID
producer_ID = input_producer_id()

# Create a datagram socket
producer_socket = UDM_Socket("producer")
  
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
                send_data(packet_type_frame, producer_ID, stream_number, i+1, payload_frame, producer_socket, BROKER_ADDRESS)

                # send audio data
                if has_audio:
                    audio_encode = result_input_audio[1]
                    audio_chunk_size = result_input_audio[2]
                    payload_audio = audio_encode[i * audio_chunk_size:(i + 1) * audio_chunk_size]
                    send_data(packet_type_audio, producer_ID, stream_number, i+1, payload_audio, producer_socket, BROKER_ADDRESS)

    elif action_input == '3':
        break
    else:
        print("Invalid action")