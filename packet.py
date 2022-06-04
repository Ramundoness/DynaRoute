from message import Message

class Packet:
    '''
    Packet class. The information transmitted between nodes in the network. Wraps around a Message
        object.
    '''
    def __init__(self, msg: Message, ttl=0) -> None:
        self.message = msg      # Message object that is in transit to its destination
        self.nodes_visited = []     # Nodes the messages has visited, in order
        self.ttl = ttl      # Whether to use TTL to limit stale packets