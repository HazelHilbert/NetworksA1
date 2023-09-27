import socket
from client import *
from header import *

localIP     = "broker"
localPort   = 50000
bufferSize  = 1024

msgFromServer       = "Received"

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP broker up and listening")

producers = []
consumers = []

# Listen for incoming datagrams
while(True):
    print(producers)
    print(consumers)

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
            if producer.producer_name == producer_id:
                known_producer = True
                producer.add_stream(producer_id+stream_number)
                producer.list_streams()
        if not known_producer:
            new_producer = Producer(producer_id)
            new_producer.add_stream(producer_id+stream_number)
            producers.append(new_producer)
            new_producer.list_streams()
        
    elif packet_type == 2:
        message_start = "Received producer: "
    
    elif 3 <= packet_type <= 6:
        producer_id = get_producer_id(header)
        if packet_type == 5 or packet_type == 6:
            stream_number = get_stream_number(header)

        known_producer = False
        for producer in producers:
            if producer.producer_name == producer_id:
                known_producer = True
                the_producer = producer
        if not known_producer:
            message_start = "ERROR: not a known producer: "
            msgFromServer = "ERROR: not a known producer"
        
        else:
            known_consumer = False
            for consumer in consumers:
                if address == consumer.ip_address:
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

            elif packet_type == 5:
                message_start = "Consumer sub stream: "
                current_consumer.subscribe(producer_id+stream_number)

            elif packet_type == 6:
                message_start = "Consumer unsub stream: "
                current_consumer.unsubscribe(producer_id+stream_number)
            
            current_consumer.list_subscriptions()
    else:
        message_start = "ERROR "

    producertMsg = message_start + format(payload.decode('utf-8'))
    producerIP  = "IP Address:{}".format(address)
    
    print(producertMsg)
    print(producerIP)

    # Sending a reply
    UDPServerSocket.sendto(str.encode(msgFromServer), address)
