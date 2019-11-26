from Block import *
from Node import *
from Network import *
import random
import datetime
import math

class Simulator:


  def __init__(self, num_nodes, duration, gossip_factor):
    self.duration = datetime.timedelta(hours=duration)
    self.time_passed = datetime.timedelta(0)
    self.network = Network(num_nodes)
    self.num_nodes = num_nodes
    self.nodes = []

    r = [random.random() for i in range(num_nodes)]
    s = sum(r)
    hp = [i/s for i in r]

    time = datetime.datetime.now()

    for i in range(num_nodes):
      self.nodes.append(Node(i, time, 1))

    self.network.set_uniform_gossip_factor(gossip_factor)


  def run_simulation(self):
    for n in self.nodes:
      n.create_block_event()
      #n.print_stats()

    counter = 0
    log_interval = datetime.timedelta(minutes=10)
    while self.time_passed < self.duration:
      nodes, time_interval = self.get_next_nodes()

      for n in nodes:
        neighbours = self.get_random_neighbours(n)
        n.update_neighbours(neighbours)
        n.process_event()

      self.time_passed += time_interval
      #print("{} has passed".format(self.time_passed))
      if self.time_passed // log_interval > counter:
        counter += 1
        print("{} minutes has passed".format(counter * 10))
    print("Simulation complete!")
    for n in self.nodes:
      n.draw_dag()
      n.print_stats()


  def get_next_nodes(self):
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
    node_ids = self.network.random_neighbours(node.id)
    return [self.nodes[i] for i in range(self.num_nodes)]

if __name__ == "__main__":
  random.seed(1234)
  sim = Simulator(100, 1, 5)
  sim.run_simulation()
