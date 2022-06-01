class Message:
    def __init__(self, id, start_id, destination_id) -> None:
        self.id = id
        self.start = start_id
        self.destination_id = destination_id
        self.total_cost = 0
        self.delivered = False
        self.num_packets = 0    # number of packets per message

        # can store other things like metrics
        # figure out what total cost is work done by network or number of steps taken for message to its destination
        # congestion vs latency