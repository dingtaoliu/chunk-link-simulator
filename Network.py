from Node import *
import networkx as nx 
import random 

class Network:

  def __init__(self, num_nodes):
    self.graph = nx.complete_graph(num_nodes)
    for i in range(num_nodes):
      self.graph.nodes[i]['node'] = Node(i)
  

  # gossip factor is how many neighbours each node will gossip to 
  def set_uniform_gossip_factor(self, factor):
    num_nodes = len(self.graph.nodes)
    for i in range(num_nodes):
      self.graph.nodes[i]['gossip_factor'] = factor 
  
  def gossip_block(self, node_id):
    gossip_factor = self.graph.nodes[node_id]['gossip_factor']

    node_ids = list(range(len(self.graph.nodes)))
    node_ids.remove(node_id)
    random.shuffle(node_ids)
    # print(node_ids)
    node_ids = node_ids[:gossip_factor]
    nodes = [d['node'] for b,d in self.graph.nodes(data=True) if b in node_ids]
    self.graph.nodes[node_id]['node'].gossip_block(nodes)

if __name__ == "__main__":
  net = Network(5)
  net.set_uniform_gossip_factor(3)
  for i in range(100):
    node_id = random.choice(range(5))
    net.gossip_block(node_id)

  for node_id, data in net.graph.nodes(data=True):
    data['node'].draw_dag()
  

  



