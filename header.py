import struct

def make_header_1(packet_type, producer_ID, stream_number):
    return struct.pack(get_header_format(packet_type), packet_type, producer_ID, stream_number)

def make_header_2(packet_type, producer_ID, stream_number, frame, payload_size):
    return struct.pack(get_header_format(packet_type), packet_type, producer_ID, stream_number, frame, payload_size)

def make_header_3(packet_type, producer_ID):
    return struct.pack(get_header_format(3), packet_type, producer_ID)

def get_header_format(header):
    if type(header) == int:
        packet_type = header
    else:
        packet_type = header[0]

    if packet_type == 1 or packet_type == 5 or packet_type == 6:
        header_format = 'b 6s b'
    elif packet_type == 2:
        header_format = 'b 6s b i i'
    elif packet_type == 3 or packet_type == 4:
        header_format = 'b 6s'

    return header_format
    
def get_header_length(header):
    return struct.calcsize(get_header_format(header))

def get_producer_id(header):
    return struct.unpack(get_header_format(header), header)[1].decode('utf-8')

def get_stream_number(header):
    return str(struct.unpack(get_header_format(header), header)[2])
