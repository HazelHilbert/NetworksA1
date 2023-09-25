import struct

def make_header_1(packet_type, producer_ID, stream_number):
    return struct.pack(get_header_format(packet_type), packet_type, producer_ID, stream_number)

def make_header_2(packet_type, producer_ID, stream_number, frame, payload_size):
    return struct.pack(get_header_format(packet_type), packet_type, producer_ID, stream_number, frame, payload_size)
    
def get_header_format(header):
    if type(header) == int:
        packet_type = header
    else:
        packet_type = header[0]

    if packet_type == 1:
        header_format = 'b 6s b'
    elif packet_type == 2:
        header_format = 'b 6s b i i'
    return header_format
    
def get_header_length(header):
    return struct.calcsize(get_header_format(header))
