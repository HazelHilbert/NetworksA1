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
    #st = "Prod: "
    #for p in producers:
    #    st += p.producer_id + " " 
    #print(st)
    #st = "Con: "
    #for c in consumers:
    #    st += str(c.address) + " " 
    #print(st)
    
    data = broker_socket.receive_data_parsed()
    packet_type = data[0]
    header = data[1]
    payload = data[2]
    address = data[3]
    
    msgFromServer = "Received"

    message_start = ''
    if packet_type == 1:
        message_start = "Announced producer: "
        producer_id = get_producer_id(header)
        stream_number = get_stream_number(header)

        known_producer = False
        for producer in producers:
            if producer.producer_id == producer_id:
                known_producer = True
                producer.add_stream(producer_id+stream_number)
                #print("producers streams")
                #producer.list_streams() #
        if not known_producer:
            new_producer = Producer(producer_id)
            new_producer.add_stream(producer_id+stream_number)
            producers.append(new_producer)
            #print("producers streams")
            #new_producer.list_streams()
        
    elif packet_type == 2:
        message_start = "Received from producer: "
    
    elif 3 <= packet_type <= 6:
        producer_id = get_producer_id(header)

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
            #print("consumer subs")
            #current_consumer.list_subscriptions()
    
    else:
        message_start = "ERROR "

    # print received data
    if packet_type != 2:
        print(message_start + format(payload.decode('utf-8')))
        print("IP Address:{}".format(address))

    # foward frames to consumers
    if packet_type == 2:
        print(message_start + str(producer_id) + "; stream: " + str(stream_number) + "; frame: " + str(get_frame_number(header)))
        print("IP Address:{}".format(address))

        producer_stream = get_producer_id(header) + get_stream_number(header)
        print("Fowarding stream to consumers")
        #new_header = 7 + header[1:]
        for consumer in consumers:
            if producer_stream in consumer.subscriptions:
                broker_socket.send_data_to(header + payload, consumer.address)
                print("Message from consumer " + str(consumer.address[0]) + ": " + broker_socket.receive_data().decode('utf-8'))
    
    # send a reply
    broker_socket.send_data_to(str.encode(msgFromServer), address)

