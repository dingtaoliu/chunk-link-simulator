import networkx as nx 
import matplotlib.pyplot as plt
import random
import heapq
import datetime 

from Node import *

ATTACK_START_LEN = 3
ATTACK_DISTANCE = 2

class DSNode(Node):

  def __init__(self, identifier, time, hash_power, master = None, upload_bandwidth=5):
    Node.__init__(self, identifier, time, hash_power, master, upload_bandwidth)

    self.attack_block = None

  def get_candidates(self):
    print('xd')
    if Block.METHOD == "longest_chain":
      longest_chain = self.get_main_chain_blocks()
      if len(longest_chain) < ATTACK_START_LEN:
        print("longest chain",  self.get_longest_chain_blocks())
        return self.get_longest_chain_blocks()
      elif self.attack_block is not None:
        print("Attack_block is not none")
        print(self.attack_block)
        depth = self.block_dag.nodes[self.attack_block]['depth']
        tree = nx.bfs_tree(self.block_dag, self.attack_block)
        nodes = tree.nodes
        max_len = len(nx.dag_longest_path(tree)) + depth - 1
        # print("Printing the depth and  max length and tree.")
        # print(depth)
        # print(max_len)
        # print(list(tree.nodes()))
        return [b for b,d in self.block_dag.nodes(data=True) if (d['depth'] == max_len) and (b in nodes)]
        #return [self.attack_block]
      elif len(longest_chain) >= ATTACK_START_LEN and self.attack_block is None:
        self.attack_block = longest_chain[ATTACK_START_LEN - ATTACK_DISTANCE]
        print("Starting attack on block {}".format(self.attack_block))
        return [self.attack_block]
      else:
        print("The else case")
        return [self.attack_block]

  def get_main_chain_blocks(self):
    # for b, d in self.block_dag.nodes(data=True):
    #   print(d)
    tree = nx.bfs_tree(self.block_dag, "genesis")
    nodes = tree.nodes
    return nx.dag_longest_path(tree)



  def create_block(self, block):
    """
    The simulator notifies this node to
    create a new block. This node will:
      1. append to local DAG
      2. cache this block locally
      3. gossip to neighbours

    Parameters
    ----------
    block : Block
        The newly created block instance.
    """
    if self.attack_block is None:
        Node.create_block(self,block)
    else:
        print("Node {} generated block {} at time {}".format(self.id, block.block_hash, self.time))
        self.append_block(block)
        self.master.append_block(block)
        candidates = self.get_candidates()
        
        if block.prev_hash in candidates:
            self.created_blocks.append(block.block_hash)
            if self.attack_block is not None:
              self.attack_block = block.block_hash

            self.gossip_buffer.append(block)
        self.create_block_event()


  def process_event(self):
    """
    Process events in the local event queue. This will check if we are "able" to process the
    nearest future events (i.e. if local time has passed the event time)
    """
    if self.attack_block is None:
        Node.process_event(self)
    else:
        # update current timestamp
        self.time = self.event_buffer[0].timestamp
        
        # if not self.event_buffer:
        #     return
        
        # check if any events should be processed
        print(self.event_buffer[0].event_type)
        while self.event_buffer[0].timestamp <= self.time:

          event = heapq.heappop(self.event_buffer)

          if event.event_type == EventType.CREATE_BLOCK:
            self.create_block(event.block)
          else:
            self.append_block(event.block)
            if event.block not in self.known_blocks:
              self.gossip_buffer.append(event.block)
          
            # candidates = self.get_candidates()
            
            # if self.best_block not in candidates:
            #   self.create_block_event()

          self.clean_event_buffer(event.block)
          self.known_blocks.append(event.block)
    
    self.gossip_block()
