import networkx as nx 
import matplotlib.pyplot as plt
import random
import heapq
import datetime 

from Block import *
from networkx.drawing.nx_agraph import graphviz_layout
from Network import *

class Node: 

  def __init__(self, identifier, time, upload_bandwidth=5):
    self.id = identifier
    self.block_dag = nx.DiGraph()
    self.block_dag.add_node("genesis", depth=1, prev = 'lol')
    self.new_block = None

    # list of blocks seen by this node
    self.known_blocks = []
    
    # heap of tuples of the form (timestamp, event)
    self.event_buffer = []

    # list of blocks to buffer
    self.gossip_buffer = []

    # MB/s upload speed
    # assuming each block is 1 MB, this is the number of blocks  that can be gossiped per second
    self.upload_bandwidth = upload_bandwidth

    self.time = time

    self.neighbours = None

  def append_block(self, block):
    # skip if block is already seen
    if block.block_hash in self.block_dag.nodes:
      return

    prev_block = block.prev_hash
    self.latest_block = block

    # if parent block has been seen
    if prev_block in self.block_dag.nodes:
      prev_depth = self.block_dag.nodes[prev_block]['depth']
      self.block_dag.add_node(block.block_hash, depth = prev_depth + 1, block = block, prev = prev_block)
      self.block_dag.add_edge(prev_block, block.block_hash) 
    
    # if parent block have not yet been seen
    else:
      self.block_dag.add_node(block.block_hash, prev = block.prev_hash, depth=1)
    
    # if we are connecting a disjoint graph with the main graph
    depth = self.block_dag.nodes[block.block_hash]['depth']
    children = [b for b,d in self.block_dag.nodes(data=True) if d['prev'] == block.block_hash]
    if children != []:
      for c in children:
        self.block_dag.add_edge(block.block_hash, c)
        tree = nx.bfs_tree(self.block_dag, c)
        for node in tree.nodes:
          self.block_dag.nodes[node]['depth'] += depth


  def create_block(self):
    self.append_block(self.new_block)
    self.create_block_event()


  def gossip_block(self):
    #self.create_block("longest_chain")
    for node in self.neighbours:
      counter = 0
      node_time = node.time
      # gossip all blocks in buffer
      # can be tweaked to only gossip blocks not yet gossipped 
      while self.gossip_buffer:
        print("gossipping")
        print(len(self.gossip_buffer))
        block = self.gossip_buffer.pop()

        # dont gossip to nodes that have already seen this node
        if block in node.known_blocks:
          break
        
        # generate receive timestamp 
        delay = datetime.timedelta(seconds=(counter // self.upload_bandwidth))

        timestamp = node_time + delay + Network.AVERAGE_NETWORK_DELAY

        heapq.heappush(node.event_buffer, (timestamp, block))

  def process_event(self, timedelta):
    # update current timestamp
    self.time = self.time + timedelta

    # check if any events should be processed
    while self.event_buffer[0][0] <= self.time:
      print("processing event queue of {}".format(self.id))
      print(len(self.event_buffer))
      block = heapq.heappop(self.event_buffer)[1]

      if block == self.new_block:
        self.create_block()
      else:
        self.append_block(block)

      self.gossip_buffer.append(block)
      self.gossip_block()

  def create_block_event(self):
    # figure out when to generate the next block
    time_to_generate = random.expovariate(Block.AVG_GEN_TIME)
    timestamp = self.time + datetime.timedelta(minutes=time_to_generate)

    candidates = []
    # figure out where to append this block
    if Block.METHOD == "longest_chain":
      candidates = self.get_longest_chain_blocks()

    # tie breaker
    parent = random.choice(candidates)
    block = Block(parent)

    self.new_block = block 

    heapq.heappush(self.event_buffer, (timestamp, self.new_block))
  
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
    plt.savefig("{}_block_dag.png".format(self.id))

    # clear the figure or else subsequent graphs will be combined for some reason
    plt.clf()

  # returns the time until the next event 
  def next_interval(self):
    timestamp = self.event_buffer[0][0]
    timedelta = timestamp - self.time 
    return timedelta

  def update_neighbours(self, nodes):
    self.neighbours = nodes

if __name__ == "__main__":
  n = Node("test")
  n.create_block("longest_chain")
  n.create_block("longest_chain")
  n.draw_dag()
