import random
from message import Message

class Workload:
    def __init__(self, num_messages, num_nodes) -> None:
        self.num_message = num_messages
        self.num_nodes = num_nodes
        self.messages = self.generate_messages()
    
    def generate_messages(self):
        '''Generates messages with random start and destination.'''
        for i in range(self.num_messages):
            message = Message(
                id=i, 
                start_id=random.randint(0, self.num_nodes),
                destination_id=random.randint(0, self.num_nodes)
            )
            self.messages.append(message)
    