import networkx as nx 
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import random
from Block import *

class Node: 

  def __init__(self, identifier):
    self.id = identifier
    self.block_dag = nx.DiGraph()
    self.block_dag.add_node("genesis", depth=1, prev = 'lol')
    self.last_block = None
    self.block_buffer = []

  def append_block(self, block):
    if block.block_hash in self.block_dag.nodes:
      return

    prev_block = block.prev_hash
    self.latest_block = block

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
        for node in tree.nodes:
          self.block_dag.nodes[node]['depth'] += depth


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
    #self.create_block("longest_chain")
    if not self.last_block:
      return
    for node in nodes:
      node.append_block(self.last_block)

  
  def get_longest_chain_blocks(self):
    # for b, d in self.block_dag.nodes(data=True):
    #   print(d)
    tree = nx.bfs_tree(self.block_dag, "genesis")
    nodes = tree.nodes
    max_len = len(nx.dag_longest_path(tree))
    return [b for b,d in self.block_dag.nodes(data=True) if (d['depth'] == max_len) and (b in nodes)]

  
  def draw_dag(self):
    position = graphviz_layout(self.block_dag, prog='dot')
    #print(self.block_dag)
    nx.draw(self.block_dag, position, with_labels=True, arrows=True, scale=100)
    plt.savefig("../{}_block_dag.png".format(self.id))

    # clear the figure or else subsequent graphs will be combined for some reason
    plt.clf()

if __name__ == "__main__":
  n = Node("test")
  n.create_block("longest_chain")
  n.create_block("longest_chain")
  n.draw_dag()
