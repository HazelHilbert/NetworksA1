import socket
from client import *
from header import *
from send_data import *

localIP     = "broker"
localPort   = 50000
bufferSize  = 1024

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

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
    
    msgFromServer = "Received"

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    data = bytesAddressPair[0]
    address = bytesAddressPair[1]
    packet_type = data[0]

    header = data[:get_header_length(data)]
    payload = data[get_header_length(data):]

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
        message_start = "Received producer: "
    
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

    producertMsg = message_start + format(payload.decode('utf-8'))
    producerIP  = "IP Address:{}".format(address)
    
    print(producertMsg)
    print(producerIP)

    # Sending a reply
    UDPServerSocket.sendto(str.encode(msgFromServer), address)
