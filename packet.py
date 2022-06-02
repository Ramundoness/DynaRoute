from message import Message

class Packet:
    def __init__(self, msg: Message, ttl=0) -> None:
        self.message = msg
        self.nodes_visited = [] # Nodes the messages has visited, in order.
        self.ttl = ttl # remember to set the ttl for new messages if the alrgorithm uses it

    def get_num_hops(self) -> int:
        return len(self.nodes_visited)
