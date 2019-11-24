from Block import *
from Node import *
from Network import *
import random
import datetime

class Simulator:


  def __init__(self, num_nodes, duration, gossip_factor):
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
    for n in self.nodes:
      n.create_block_event()

    while self.time_passed < self.duration:
      time_interval = self.get_next_interval()

      for n in self.nodes:
        neighbours = self.get_random_neighbours(n)
        n.update_neighbours(neighbours)
        n.process_event(time_interval)

      self.time_passed += time_interval
      print("../graphs/{} has passed".format(self.time_passed))
    print("Simulation complete!")
    for n in self.nodes:
      n.draw_dag()


  def get_next_interval(self):
    intervals = []
    for n in self.nodes:
      intervals.append(n.next_interval())
    return min(intervals)

  def get_random_neighbours(self, node):
    node_ids = self.network.random_neighbours(node.id)
    return [self.nodes[i] for i in range(self.num_nodes)]

if __name__ == "__main__":
  sim = Simulator(5, 1, 5)
  sim.run_simulation()