import os

# Ask for producer ID
def input_producer_id(sub=False):
    valid = False
    while not valid:
        input_message = "Enter producer ID: "
        if sub:
            input_message = "Enter producer ID to subscribe/unsubscribe to: "
        id_input = input(input_message)
        if len(id_input) == 6:
            try:
                producer_ID = bytes.fromhex(id_input)
                valid = True
            except:
                print("Invalid ID: enter 6 char string representing a 3 byte hexadecimal number")
                continue
        else:
            print("Invalid ID: enter 6 char string representing a 3 byte hexadecimal number")
    return producer_ID

def input_producer_id_sub():
    return input_producer_id(True)   

# Anounce and add stream
def input_new_stream(stream_list):
    return stream_help(stream_list, True)

# Check stream
def input_stream(stream_list):
    return stream_help(stream_list, False)

def stream_help(stream_list, is_new):
    valid = False
    while not valid:
        try:
            stream_input = int(input("Enter stream number: "))
            if 0 <= stream_input <= 127:
                valid = True
                stream_number = stream_input
                if is_new:
                    stream_list.append(stream_number)
                if stream_number not in stream_list:
                    print("Please announce stream before publishing content")
                    return -1
            else:
                print("Invalid stream number: enter int [0, 127]")
        except:
            if valid == False:
                print("Invalid stream number: enter int [0, 127]")
    return stream_number

# get input for frames
def input_frames():
    valid = False
    while not valid:
        try:
            folder_input = input("Enter folder with frames to broadcast: ")
            list_of_frames = os.listdir(os.getcwd() + '/' + folder_input)
            valid = True
        except:
            if (valid == False):
                print("Could not find folder")
    return (folder_input, list_of_frames)

# get input for audio
def input_audio(list_of_frames):
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
                audio_encode = None
                audio_chunk_size = None
                valid = True
            elif (valid == False):
                print("Could not find audio file")
    return (has_audio, audio_encode, audio_chunk_size)
