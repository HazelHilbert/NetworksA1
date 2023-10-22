import socket, random, zlib
from header import *

BROKER_ADDRESS = ("broker", 50000)

class UDM_Socket:
    def __init__(self, name):
        self.UDPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.bufferSize = 65536
        self.name = name

    def bind_to_address(self, addressPort):
        self.UDPSocket.bind(addressPort)

    def set_timeout(self, timeout):
        self.UDPSocket.settimeout(timeout)
    
    def send_data_to(self, bytesToSend, addressPort):
        self.UDPSocket.sendto(bytesToSend, addressPort)
    
    def receive_data(self):
        return self.UDPSocket.recvfrom(self.bufferSize)[0]

    def receive_data_parsed(self):
        data = self.UDPSocket.recvfrom(self.bufferSize)
        
        packet_type = data[0][0]
        header = data[0][:get_header_length(packet_type)]
        payload = data[0][get_header_length(packet_type):]
        address = data[1]

        return (packet_type, header, payload, address)
    
# sends data with flow control
def send_data(packet_type, producer_ID, stream_number, frame_number, payload, sender_socket, receiver_address):
    sender_socket.set_timeout(0.1)
    
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
        sender_socket.send_data_to(header + payload_corrupted, receiver_address)
        
        # try to recive response
        try:
            response_data = sender_socket.receive_data_parsed()
            response_packet_type = response_data[0]
            response_payload = response_data[2]
            if response_packet_type == 7:
                print("Acknowledgment: " + response_payload.decode('utf-8'))
                response_received = True
            else:
                print("Negative response, retransmitting frame", frame_number)
        except:
            print("No response in time, retransmitting frame", frame_number)
    
    sender_socket.set_timeout(None)
    