from Block import *
from Node import *
from Network import *
import random
import datetime
import math

class Simulator:


  def __init__(self, num_nodes, duration, num_neighbours):
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
    num_neighbours : int
        Number of neighbors per nodes.
    """
    self.duration = datetime.timedelta(hours=duration)
    self.time_passed = datetime.timedelta(0)
    self.network = Network(num_nodes, num_neighbours)
    self.num_nodes = num_nodes
    self.nodes = []

    r = [random.random() for i in range(num_nodes)]
    s = sum(r)
    hp = [i/s for i in r]

    time = datetime.datetime.now()
    self.master = Node("master", time, 9001)

    for i in range(num_nodes):
      self.nodes.append(Node(i, time, hp[i], self.master))

    avg = 0
    for i in range(num_nodes):
      avg += self.nodes[i].block_rate
    print("AVG BLOCK RATE IS {}".format(avg))
    #self.network.set_uniform_gossip_factor(gossip_factor)


  def run_simulation(self):
    """
    Runs the simulation. 
    """
    # I dont think this is a bug though. Every node is expected to generate one block/h
    # we got 1k nodes => expected to generate 1k blocks within a hour
    for n in self.nodes:
      neighbours = self.get_neighbours(n.id)
      n.update_neighbours(neighbours)
      n.create_block_event()
      #n.print_stats()

    counter = 0
    iterations = 0
    log_interval = datetime.timedelta(minutes=10)
    while self.time_passed < self.duration:
      iterations += 1

      nodes, time_interval = self.get_next_nodes()

      for n in nodes:
        n.process_event()

      self.time_passed += time_interval
      #print("{} has passed".format(self.time_passed))
      if self.time_passed // log_interval > counter:
        counter += 1

        #print("{} minutes has passed".format(counter * 10))
    #print("Simulation complete!")
    #print("{} total iterations".format(iterations))
    # i = 0
    # for n in self.nodes:
    #   i += 1
    #   if i % 10 == 0:

    #     n.draw_dag()
    #     n.print_stats()
    print("Hello there")
    print(self.time_passed)
    total_blocks = len(self.master.block_dag.nodes)
    #print("{} blocks generated in total!".format(total_blocks))
    self.master.draw_dag()

    for i in self.nodes:
      i.observe_create_events()

    for i in self.nodes:
      print("current time for node {} is {}".format(i.id, i.time))

    return total_blocks


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

  def get_neighbours(self, node):
    node_ids =  self.network.neighbours(node)
    return [self.nodes[i] for i in range(self.num_nodes)]

if __name__ == "__main__":
  #random.seed(1234)
  mean = 0
  for i in range(10):
    Block.counter = 1
    sim = Simulator(2, 24,2)
    mean += sim.run_simulation()
  print("Average num blocks generated: {}".format(mean / 50))
