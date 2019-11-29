import networkx as nx 
import matplotlib.pyplot as plt
import random
import heapq
import datetime 

from Block import *
from networkx.drawing.nx_agraph import graphviz_layout
from Network import *
from Event import *

class Node: 

  def __init__(self, identifier, time, hash_power, master = None, upload_bandwidth=5):
    self.id = identifier
    self.best_block = "genesis"
    self.block_dag = nx.DiGraph()
    self.block_dag.add_node("genesis", depth=1, prev = 'lol')
    self.created_blocks = []
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

    self.gossip_hash = {}

    self.hash_power = hash_power

    self.block_time = 1 / self.hash_power * Block.AVG_GEN_TIME

    self.master = master


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


  def create_block(self, block):
    candidates = []

    if Block.METHOD == "longest_chain":
      candidates = self.get_longest_chain_blocks()

    if block.prev_hash in candidates:
        #print("Node {} generated block {}".format(self.id, block.block_hash))
        self.append_block(block)
        self.master.append_block(block)
        self.created_blocks.append(block.block_hash)
        self.create_block_event()
        self.gossip_buffer.append(block)

  def gossip_block(self):
    #self.create_block("longest_chain")
    # gossip all blocks in buffer
    # can be tweaked to only gossip blocks not yet gossipped 
    counter = 0
    #print("Node {} has {} items to gossip".format(self.id, len(self.gossip_buffer)))
    while self.gossip_buffer:
      block = self.gossip_buffer.pop()

      #print("Neighbours: {}".format([n.id for n in self.neighbours]))
      for node in self.neighbours:
        #print(node.id)
        node_time = node.time
        # dont gossip to nodes that have already seen this node
        if block in node.known_blocks:
          continue
        
        # generate receive timestamp 
        delay = datetime.timedelta(seconds=(counter // self.upload_bandwidth))
        # delay = datetime.timedelta(0)

        timestamp = node_time + delay + Network.AVERAGE_NETWORK_DELAY
        event = Event(EventType.RECEIVE_BLOCK, block, timestamp)

        # if block.block_hash in node.gossip_hash:
          #if timestamp < node.gossip_hash[block.block_hash]:
        heapq.heappush(node.event_buffer, event)
        #print("Node {} gossips block {} to Node {}".format(self.id, block.block_hash, node.id))

        counter += 1

  def process_event(self):
    # update current timestamp
    self.time = self.event_buffer[0].timestamp
    
    if not self.event_buffer:
        return
    
    # check if any events should be processed
    #print("Node {} has {} items to process".format(self.id, len(self.event_buffer)))
    while self.event_buffer[0].timestamp <= self.time:
      #print("processing event queue of {}".format(self.id))
      #print(len(self.event_buffer))
      event = heapq.heappop(self.event_buffer)

      if event.event_type == EventType.CREATE_BLOCK:
        self.create_block(event.block)
        #print("Node {} processing create block".format(self.id))
      else:
        self.append_block(event.block)
        if event.block not in self.known_blocks:
          self.gossip_buffer.append(event.block)
        self.clean_event_buffer(event.block)
        #print("Node {} processing block {}".format(self.id, event.block.block_hash))
      
      if Block.METHOD == "longest_chain":
        candidates = self.get_longest_chain_blocks()
      
      if self.best_block not in candidates:
        self.create_block_event()

      self.known_blocks.append(event.block)
    
    self.gossip_block()

  def clean_event_buffer(self, block):
    new_buffer = []
    for event in self.event_buffer:
      if event.block != block:
        new_buffer.append(event)
    heapq.heapify(new_buffer)
    self.event_buffer = new_buffer

  def create_block_event(self):
    # figure out when to generate the next block
    #print(self.block_time)
    time_to_generate = random.expovariate(1 / self.block_time)
    timestamp = self.time + datetime.timedelta(minutes=(time_to_generate))

    candidates = []
    # figure out where to append this block
    if Block.METHOD == "longest_chain":
      candidates = self.get_longest_chain_blocks()

    # tie breaker
    parent = random.choice(candidates)
    self.best_block = parent
    block = Block(parent)
    #print("Node {} will generate block {} in {}".format(self.id, block.block_hash, time_to_generate))
    event = Event(EventType.CREATE_BLOCK, block, timestamp)

    heapq.heappush(self.event_buffer, event)
  
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
    plt.savefig("../graphs/{}_block_dag.png".format(self.id))

    # clear the figure or else subsequent graphs will be combined for some reason
    plt.clf()

  # returns the time until the next event 
  def next_interval(self):
    timestamp = self.event_buffer[0].timestamp
    timedelta = timestamp - self.time 
    return timedelta

  def update_neighbours(self, nodes):
    random.shuffle(nodes)
    self.neighbours = nodes

  def get_candidates(self):
    if Block.METHOD == "longest_chain":
      return self.get_longest_chain_blocks()


  def print_stats(self):
    print("Node {} stats: ".format(self.id))
    print(" hash power: {}".format(self.hash_power))
    print(" average block time: {}".format(self.block_time))
    print(" blocks generated: {}".format(len(self.created_blocks)))
    print(" event buffer size: {}".format(len(self.event_buffer)))

  def update_master(self, master, block):
    master.append_block(block)



if __name__ == "__main__":
  n = Node("test")
  n.create_block("longest_chain")
  n.create_block("longest_chain")
  n.draw_dag()
