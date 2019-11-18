import networkx as nx 
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import random

class Node: 

  # unconfirmed transactions pool
  tx_pool = []

  # genesis block 
  gen_block = None

  # time stamp
  timestap = None

  def __init__(self, identifier):
    self.id = identifier
    self.block_dag = nx.DiGraph()
    self.block_dag.add_node("genesis", depth=1)
  
  def append_block(self, block, prev_block):
    prev_depth = self.block_dag.nodes[prev_block]['depth']
    self.block_dag.add_node(block.block_hash, depth = prev_depth + 1, block = block)
    self.block_dag.add_edge(prev_block, block.block_hash) 


  def create_block(self, method):
    if method == 'longest_chain':
      candidates = candidates = self.get_longest_chain_blocks(self):

      # tie breaker
      # chose randomly as a placeholder
      parent = random.choice(candidates)
      block = Block()
      self.append_block(block, parent)

  
  def get_longest_chain_blocks(self):
    max_len = len(nx.dag_longest_path(self.block_dag))
    return [b for b,d in self.block_dag.nodes(data=True) if d['depth'] == max_len]

  
  def draw_dag(self):
    position = graphviz_layout(self.block_dag, prog='dot')
    nx.draw(self.block_dag, position, arrows=True)
    plt.savefig("/graphs/{}_block_dag.png".format(self.id))

    # clear the figure or else subsequent graphs will be combined for some reason
    plt.clf()

