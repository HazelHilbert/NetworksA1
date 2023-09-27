class Producer:
    def __init__(self, producer_name):
        self.producer_name = producer_name
        self.streams = []

    def add_stream(self, stream_number):
        if stream_number not in self.streams:
            self.streams.append(stream_number)

    def remove_stream(self, stream_number):
        if stream_number in self.streams:
            self.streams.remove(stream_number)

    def list_streams(self):
        print(self.streams)

class Consumer:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.subscriptions = []

    def subscribe(self, producer_stream):
        if producer_stream not in self.subscriptions:
            self.subscriptions.append(producer_stream)

    def unsubscribe(self, producer_stream):
        if producer_stream in self.subscriptions:
            self.subscriptions.remove(producer_stream)

    def subscribeAll(self, producer):
        for stream in producer.streams:
            self.subscribe(producer.producer_name+stream)

    def unsubscribeAll(self, producer):
        for stream in producer.streams:
            self.unsubscribe(producer.producer_name+stream)

    def list_subscriptions(self):
        print(self.subscriptions)