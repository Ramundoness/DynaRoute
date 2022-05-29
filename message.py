class Message:
    def __init__(self, id, start_id, destination_id) -> None:
        self.id = id
        self.start = start_id
        self.destination_id = destination_id
        self.total_cost = 0
        self.delivered = False
        self.nodes_visited = [] # Nodes the messages has visited, in order.