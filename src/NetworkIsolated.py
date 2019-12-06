from Node import *
import networkx as nx 
import random 

import datetime

class NetworkIsolated(Network):

  # average delay 
  AVERAGE_NETWORK_DELAY = datetime.timedelta(seconds=12)

  def __init__(self, num_nodes, num_neighbours, num_isolated, seed=1234):
    """
    Network class.

    Parameters
    ----------
    num_nodes : int
        Num of nodes in this network.
    num_neighbours : int
        Number of neighbours per node.
    seed : int
        Seed
    """

    # We subtract isolated nodes from total nodes
    self.graph = nx.fast_gnp_random_graph(num_nodes - num_isolated, num_neighbours / (num_nodes - num_isolated))
    for i in range(num_isolated):
      curr_id = i + num_nodes - num_isolated
      self.graph.add_node(curr_id)
      k = random.randint(0, (num_nodes - num_isolated) - 1)
      self.graph.add_edge(curr_id, k)
    
    position = graphviz_layout(self.graph, prog='dot', args='-Gnodesep=5 -Granksep=5 -Gpad=1')
    nx.draw(self.graph, position, with_labels=True, arrows=True, node_size=100, font_size=8)
    plt.savefig("network.png")
    plt.clf()



  
  # gossip factor is how many neighbours each node will gossip to 
  # def set_uniform_gossip_factor(self, factor):
  #   """
  #   Sets the gossip factor of this network.
  #   Gossip factor is how many neighbours each node will gossip to.

  #   Parameters
  #   ----------
  #   factor : int
  #       ID of this node.
  #   """
  #   num_nodes = len(self.graph.nodes)
  #   for i in range(num_nodes):
  #     self.graph.nodes[i]['gossip_factor'] = factor 

  # def random_neighbours(self, node_id):
  #   """
  #   Get a random subset of the node's neighbours.

  #   Parameters
  #   ----------
  #   node_id : str
  #       ID of this node.
  #   """
  #   gossip_factor = self.graph.nodes[node_id]['gossip_factor']
  #   node_ids = list(range(len(self.graph.nodes)))
  #   node_ids.remove(node_id)
  #   random.shuffle(node_ids)
  #   return node_ids[:gossip_factor]
  # 
  # def neighbours(self, node_id):
  #   return [n for n in self.graph[node_id]]



# if __name__ == "__main__":
#   net = Network(1000)
#   net.set_uniform_gossip_factor(900)
#   num_nodes = len(net.graph.nodes)
#   for i in range(50):
#     node_id = random.choice(range(5))
#     net.graph.nodes[node_id]['node'].create_block("longest_chain")

#     for i in range(num_nodes):
#       net.gossip_block(i)

#   for node_id in list(net.graph.nodes)[:10]:
#     net.graph.nodes[node_id]['node'].draw_dag()
  
# 6 - 8 pages report
  



