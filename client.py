class Producer:
    def __init__(self, producer_id):
        self.producer_id = producer_id
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
    def __init__(self, address):
        self.address = address
        self.subscriptions = []

    def subscribe(self, producer_stream):
        if producer_stream not in self.subscriptions:
            self.subscriptions.append(producer_stream)

    def unsubscribe(self, producer_stream):
        if producer_stream in self.subscriptions:
            self.subscriptions.remove(producer_stream)

    def subscribeAll(self, producer):
        for stream in producer.streams:
            self.subscribe(stream)

    def unsubscribeAll(self, producer):
        for stream in producer.streams:
            self.unsubscribe(stream)

    def list_subscriptions(self):
        print(self.subscriptions)