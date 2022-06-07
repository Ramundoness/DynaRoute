class Message:
    '''
    Message class. Contains the raw information that needs to be passed from the start node to the
        end node. Currently, the messages themselves contain no real valuable information (only routing
        deetails and cost metrics).
    '''
    def __init__(self, id, start_id, destination_id) -> None:
        self.id = id        # Integer id of the message
        self.start = start_id       # Integer id of the start node
        self.destination_id = destination_id    # Integer id of the destination node
        self.total_cost = 0     # Cumulative sum of "hops" for this message to be delivered
        self.delivered = False     # Whether the message has been delivered or not
        self.num_packets = 0    # Number of packets per message