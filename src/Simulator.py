from Block import *
from Node import *
from DSNode import *
from Network import *
import random
import datetime
import math

class Simulator:


  def __init__(self, num_nodes, duration, num_neighbours, malicious = [], draw_dags=False):
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
    self.hon_node_ids = []
    self.mal_node_ids = []
    self.draw_dags = draw_dags

    num_mal = len(malicious)
    num_hon = num_nodes - num_mal 

    r = [random.random() for i in range(num_hon)]
    mal_power = sum(malicious)
    hon_power = 1 - mal_power
    s = sum(r)
    hp = [(i * hon_power) / s for i in r]
    print("total power: {}".format(sum(hp) + mal_power))

    time = datetime.datetime.now()
    self.master = Node("master", time, 9001)

    avg = 0
    for i in range(num_hon):
      node = Node(i, time, hp[i], self.master)
      self.nodes.append(node)
      avg += node.block_rate
      self.hon_node_ids.append(i)

    i += 1
    for m in malicious:
      node = DSNode(i, time, m, self.master)
      self.nodes.append(node)
      avg += node.block_rate
      self.mal_node_ids.append(i)
      i += 1

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

    counter = 0
    iterations = 0
    log_interval = datetime.timedelta(minutes=10)
    while self.time_passed < self.duration:
      iterations += 1

      event_nodes, time_interval = self.get_next_nodes()

      for n in self.nodes:
        if n in event_nodes:
          n.process_event()
        else:
          n.pass_time(time_interval)

      self.time_passed += time_interval
      if self.time_passed // log_interval > counter:
        counter += 1

    print("Simulation complete!")
    print("{} total iterations".format(iterations))

    if self.draw_dags:
      for n in self.nodes:
        n.draw_dag()

    print("{} simulated".format(self.time_passed))
    total_blocks = len(self.master.block_dag.nodes)
    print("{} blocks generated in total".format(total_blocks))
    print("{} blocks abandoned".format(self.master.abandoned_blocks()))
    print("The best chain ends at {}".format(self.master.get_candidates()))
    self.draw_master()

    # for i in self.nodes:
    #   i.observe_create_events()

    # for i in self.nodes:
    #   print("current time for node {} is {}".format(i.id, i.time))

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


  def draw_master(self):
    g = self.master.block_dag

    tree = nx.bfs_tree(g, "genesis")
    longest = nx.dag_longest_path(tree)

    colours = []
    for n, data in g.nodes(data=True):
      if n == "genesis":
        colours.append("#0050bc")
        continue 
      elif n in longest and self.mal_node_ids == []:
        colours.append("#FFF233")
      else:
        block = data['block']
        colours.append(block.colour)

    position = graphviz_layout(g, prog='dot', args='-Gnodesep=5 -Granksep=5 -Gpad=1')
    nx.draw(g, 
            position, 
            with_labels=True, 
            arrows=True, 
            node_size=100, 
            font_size=8, 
            node_color=colours,
            arrowsize=5)
    plt.savefig("master_block_dag.png", dpi=300)
    plt.clf()

if __name__ == "__main__":
  #random.seed(1234)
  mean = 0
  num_runs = 1
  for i in range(num_runs):
    Block.counter = 1
    sim = Simulator(200, 3, 10, [])
    mean += sim.run_simulation()
  print("Average num blocks generated: {}".format(mean / num_runs))
