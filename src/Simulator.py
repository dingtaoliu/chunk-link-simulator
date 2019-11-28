from Block import *
from Node import *
from Network import *
import random
import datetime
import math

class Simulator:


  def __init__(self, num_nodes, duration, gossip_factor):
    """
    A Simulator that simulates the chain growing process for a
    `duration` period of time.

    Each Simulator associates one simulation of the chain.

    Parameters
    ----------
    num_bodes : str
        Num of nodes to run for this simulation.
    duration : int
        Simulation time interval.
    gossip_factor : int
        Number of neighbor nodes to broadcast to for each replaying.
    """
    self.duration = datetime.timedelta(hours=duration)
    self.time_passed = datetime.timedelta(0)
    self.network = Network(num_nodes)
    self.num_nodes = num_nodes
    self.nodes = []

    time = datetime.datetime.now()

    for i in range(num_nodes):
      self.nodes.append(Node(i, time))

    self.network.set_uniform_gossip_factor(gossip_factor)


  def run_simulation(self):
    """
    Runs the simulation. 
    """
    # I dont think this is a bug though. Every node is expected to generate one block/h
    # we got 1k nodes => expected to generate 1k blocks within a hour
    for n in self.nodes:
      n.create_block_event()

    while self.time_passed < self.duration:
      nodes, time_interval = self.get_next_nodes()

      for n in nodes:
        neighbours = self.get_random_neighbours(n)
        n.update_neighbours(neighbours)
        n.process_event()

      self.time_passed += time_interval
      print("{} has passed".format(self.time_passed))
    print("Simulation complete!")
    for n in self.nodes[0:5]:
      n.draw_dag()


  def get_next_nodes(self):
    """
    Get the next nodes to process at the next minimum timestamp.
    """
    nodes = []
    min_time = datetime.timedelta.max
    for n in self.nodes:
      interval = n.next_interval()
      if interval == min_time:
        nodes.append(n)
      elif interval < min_time:
        nodes = [n]
        min_time = interval

    return nodes, min_time

  def get_random_neighbours(self, node):
    """
    Shuffles the neighbours and return a random subset of it with 
    cardinality equal to the `gossip_factor`.
    """
    node_ids = self.network.random_neighbours(node.id)
    return [self.nodes[i] for i in range(self.num_nodes)]

if __name__ == "__main__":
  sim = Simulator(1000, 1, 20)
  sim.run_simulation()
