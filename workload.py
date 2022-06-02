import random
from message import Message

class Workload:
    def __init__(self, num_messages, num_nodes, ttl=None) -> None:
        self.num_messages = num_messages
        self.num_nodes = num_nodes
        self.messages = self.generate_messages()
        if ttl == None:
            self.ttl = num_nodes
        else:
            self.ttl = ttl
    
    def generate_messages(self):
        '''Generates messages with random start and destination.'''
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
        return sum(message.delivered for message in self.messages)
    
