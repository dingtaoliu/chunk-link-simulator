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
  net = Network(1000)
  net.set_uniform_gossip_factor(900)
  num_nodes = len(net.graph.nodes)
  for i in range(50):
    node_id = random.choice(range(5))
    net.graph.nodes[node_id]['node'].create_block("longest_chain")

    for i in range(num_nodes):
      net.gossip_block(i)

  for node_id in list(net.graph.nodes)[:10]:
    net.graph.nodes[node_id]['node'].draw_dag()
  
# 6 - 8 pages report
  



