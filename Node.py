import networkx as nx 
from networkx.drawing.nx_agraph import graphviz_layout
import pygraphviz
import matplotlib.pyplot as plt
import random
from Block import *

class Node: 

  # unconfirmed transactions pool
  tx_pool = []

  # genesis block 
  gen_block = None

  # time stamp
  timestap = None

  last_block = None

  def __init__(self, identifier):
    self.id = identifier
    self.block_dag = nx.DiGraph()
    self.block_dag.add_node("genesis", depth=1, prev = 'lol')
  
  def append_block(self, block):
    prev_block = block.prev_hash
    if prev_block in self.block_dag.nodes:
      prev_depth = self.block_dag.nodes[prev_block]['depth']
      self.block_dag.add_node(block.block_hash, depth = prev_depth + 1, block = block, prev = prev_block)
      self.block_dag.add_edge(prev_block, block.block_hash) 
    else:
      self.block_dag.add_node(block.block_hash, prev = block.prev_hash, depth=1)
    
    depth = self.block_dag.nodes[block.block_hash]['depth']
    children = [b for b,d in self.block_dag.nodes(data=True) if d['prev'] == block.block_hash]
    if children != []:
      for c in children:
        self.block_dag.add_edge(block.block_hash, c)
        tree = nx.bfs_tree(self.block_dag, c)
        for node, data in tree.nodes(data=True):
          data['depth'] += depth


  def create_block(self, method):
    if method == 'longest_chain':
      candidates = self.get_longest_chain_blocks()

      # tie breaker
      # chose randomly as a placeholder
      parent = random.choice(candidates)
      # print(parent)
      block = Block(parent)
      self.last_block = block
      self.append_block(block)

  def gossip_block(self, nodes):
    self.create_block("longest_chain")
    for node in nodes:
      node.append_block(self.last_block)

  
  def get_longest_chain_blocks(self):
    # for b, d in self.block_dag.nodes(data=True):
    #   print(d)

    max_len = len(nx.dag_longest_path(self.block_dag))
    return [b for b,d in self.block_dag.nodes(data=True) if d['depth'] == max_len]

  
  def draw_dag(self):
    position = graphviz_layout(self.block_dag, prog='dot')
    agraph = nx.nx_agraph.to_agraph(self.block_dag)
    agraph.graph_attr.update(nodesep='0.1')
    print(agraph)
    agraph.layout(prog='dot')
    position = self.get_position_from_agraph(agraph)
    #agraph.draw("graphs/{}_block_dag.png".format(self.id))
    #print(self.block_dag)
    nx.draw(self.block_dag, position, with_labels=True, arrows=True, scale=100)
    plt.savefig("graphs/{}_block_dag.png".format(self.id))

    # clear the figure or else subsequent graphs will be combined for some reason
    plt.clf()

  def get_position_from_agraph(self, agraph):
    node_pos = {}
    for n in self.block_dag:
        node = pygraphviz.Node(agraph, n)
        try:
            xx, yy = node.attr["pos"].split('.')
            node_pos[n] = (float(xx), float(yy))
        except:
            print("no position for node", n)
            node_pos[n] = (0.0, 0.0)
    return node_pos


if __name__ == "__main__":
  n = Node("test")
  n.create_block("longest_chain")
  n.create_block("longest_chain")
  n.draw_dag()
