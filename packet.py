from message import Message

class Packet:
    def __init__(self, msg: Message) -> None:
        self.message = msg
        self.nodes_visited = [] # Nodes the messages has visited, in order.

    def get_num_hops(self) -> int:
        return len(self.nodes_visited)