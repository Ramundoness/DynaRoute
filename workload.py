import random
from message import Message

class Workload:
    '''
    Workload class. Consists of the Message objects that need to be routed to their start node
        to end node destinations.
    '''
    def __init__(self, num_messages, num_nodes, ttl=None) -> None:
        self.num_messages = num_messages    # Number of messages in the workload
        self.num_nodes = num_nodes      # Number of nodes in the network
        self.messages = self.generate_messages()    # Messages that we want to send
        if ttl == None:
            self.ttl = num_nodes    # set TTL to the total number of nodes in the network
        else:
            self.ttl = ttl      # set TTL to the user-specified value
    
    def generate_messages(self):
        '''
        Function: generate_messages
            Generates messages with random start and destination.
        '''
        messages = []
        for i in range(self.num_messages):
            message = Message(
                id=i, 
                start_id=random.randint(0, self.num_nodes-1),
                destination_id=random.randint(0, self.num_nodes-1)
            )
            messages.append(message)
        return messages
    
    def num_delivered(self):
        '''
        Function: num_delivered
            Calculates the total number of messages that were delivered to their end destinations.
        '''
        return sum(message.delivered for message in self.messages)
    
