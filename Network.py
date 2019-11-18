import Node
import networkx as nx 
import random 

class Network

  def __init__(self, num_nodes):
    self.graph = nx.complete_graph(num_nodes)
    self.num_nodes = num_nodes
    for i in num_nodes:
      self.graph[i]['node'] = Node(i)
  

  # gossip factor is how many neighbours each node will gossip to 
  def set_uniform_gossip_factor(self, factor):
    num_nodes = len(self.graph.nodes)
    for i in num_nodes:
      self.graph[i]['gossip_factor'] = factor 
  
  def gossip_block(self, node_id):
    gossip_factor = self.graph[node_id]['gossip_factor']

    neighbors = list(range(self.num_nodes))
    neighbors.remove(node_id)
    neighbors = random.shuffle(neighbors)[:gossip_factor]
    
  



