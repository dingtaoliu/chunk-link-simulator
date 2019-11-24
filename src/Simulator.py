import Block
import Node 
import Network
import random

class Simulator:


  def __init__(self, num_nodes):
    self.network = Network(num_nodes)
    self.num_nodes = num_nodes

  def generate_block(self):
    node_id = random.randrange(self.num_nodes)
    self.network.propagate_block(node_id)
