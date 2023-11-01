import zlib
from client import *
from header import *
from udm_socket import *

broker_socket = UDM_Socket("broker")
broker_socket.bind_to_address(BROKER_ADDRESS)
print("UDP broker up and listening")

producers = []
consumers = []

# Listen for incoming datagrams
while(True):
    print()

    data = broker_socket.receive_data_parsed()
    packet_type = data[0]
    header = data[1]
    payload = data[2]
    address = data[3]
    producer_id = get_producer_id(header)
    producer_id_bytes = get_producer_id_bytes(header)

    # handle stream anoucment and subscriptions
    if packet_type != 2 and packet_type != 8:
        msgFromServer = "Recived"

        # Stream anouncement
        if packet_type == 1:
            message_start = "Announced producer: "
            stream_number = get_stream_number(header)

            known_producer = False
            for producer in producers:
                if producer.producer_id == producer_id:
                    known_producer = True
                    producer.add_stream(producer_id+stream_number)
            if not known_producer:
                new_producer = Producer(producer_id)
                new_producer.add_stream(producer_id+stream_number)
                producers.append(new_producer)

        # subscription handling
        elif 3 <= packet_type <= 6:
            known_producer = False
            for producer in producers:
                if producer.producer_id == producer_id:
                    known_producer = True
                    the_producer = producer
            if not known_producer:
                message_start = "ERROR: not a known producer: "
                msgFromServer = "ERROR: not a known producer"
            else:        
                if packet_type == 5 or packet_type == 6:
                    stream_number = get_stream_number(header)
                    valid_stream = True
                    if not (producer_id+str(stream_number) in the_producer.streams):
                        valid_stream = False
                        message_start = "ERROR: producer does not have stream: "
                        msgFromServer = "ERROR: producer does not have stream"
            
                known_consumer = False
                for consumer in consumers:
                    if address == consumer.address:
                        known_consumer = True
                        current_consumer = consumer
                if not known_consumer:
                    new_consumer = Consumer(address)
                    consumers.append(new_consumer)
                    current_consumer = new_consumer
                
                if packet_type == 3:
                    message_start = "Consumer sub all: "
                    current_consumer.subscribeAll(the_producer)

                elif packet_type == 4:
                    message_start = "Consumer unsub all: "
                    current_consumer.unsubscribeAll(the_producer)

                elif packet_type == 5 and valid_stream:
                    message_start = "Consumer sub stream: "
                    current_consumer.subscribe(producer_id+stream_number)

                elif packet_type == 6 and valid_stream:
                    message_start = "Consumer unsub stream: "
                    current_consumer.unsubscribe(producer_id+stream_number)
        
        else:
            message_start = "ERROR "

        # print received data if not frame or audio
        print(message_start + format(payload.decode('utf-8')))
        print("IP Address:{}".format(address))
        
        # send response
        broker_socket.send_data_to(str.encode(msgFromServer), address)

    # handle frame/audio 
    else:
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
            message_start = "ERROR: Received corrupted from producer: "
        else:
            msgFromServer = "Recived" + discription + str(get_frame_number(header))
            message_start = "Received from producer: "
        
        # print which stream/audio chunck recived
        print(message_start + str(producer_id) + "; stream: " + str(stream_number) + ";" + discription + str(get_frame_number(header)))
        #print("IP Address:{}".format(address))
        
        # send reply and foward if not corupted
        if received_crc == expected_crc:
            stream_number = get_stream_number(header)
            frame_number = get_frame_number(header)
            header = make_header(7, producer_id_bytes, int(stream_number), int(frame_number))
            payload = str.encode(msgFromServer)        
            broker_socket.send_data_to(header + payload, address)

            # foward frames to consumers
            producer_stream = get_producer_id(header) + get_stream_number(header)
            print("Fowarding stream to consumers")
            for consumer in consumers:
                if producer_stream in consumer.subscriptions:
                    # send data to each consumer and wait for responses
                    send_data(int(packet_type), producer_id_bytes, int(stream_number), int(frame_number), payload, broker_socket, consumer.address)