import struct

HEADER_FORMATS = {
    1: 'b 3s b',
    2: 'b 3s b i I',
    3: 'b 3s',
    4: 'b 3s',
    5: 'b 3s b',
    6: 'b 3s b',
    7: 'b 3s b i',
    8: 'b 3s b i I',
}

def make_header(packet_type, producer_ID, stream_number=None, frame=None, crc_value=None):
    if packet_type in {3,4}:
        return struct.pack(HEADER_FORMATS[packet_type], packet_type, producer_ID)
    elif packet_type in {1,5,6}:
        return struct.pack(HEADER_FORMATS[packet_type], packet_type, producer_ID, stream_number)
    elif packet_type in {7}:
        return struct.pack(HEADER_FORMATS[packet_type], packet_type, producer_ID, stream_number, frame)
    elif packet_type in {2,8}:
        return struct.pack(HEADER_FORMATS[packet_type], packet_type, producer_ID, stream_number, frame, crc_value)
    
def get_header_format(header):
    if type(header) == int:
        packet_type = header
    else:
        packet_type = header[0]
    return HEADER_FORMATS[packet_type]

def get_header_length(header):
    return struct.calcsize(get_header_format(header))

def get_producer_id(header):
    return str(get_producer_id_bytes(header).hex().upper())

def get_producer_id_bytes(header):
    return struct.unpack(get_header_format(header), header)[1]

def get_stream_number(header):
    return str(struct.unpack(get_header_format(header), header)[2])

def get_frame_number(header):
    return str(struct.unpack(get_header_format(header), header)[3])

def get_crc_value(header):
    return str(struct.unpack(get_header_format(header), header)[4])