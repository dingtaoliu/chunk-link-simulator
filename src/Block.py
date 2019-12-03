import uuid 

class Block:
  
  # counter
  counter = 1

  # number of minutes per block
  AVG_GEN_TIME = 10

  METHOD = "longest_chain"

  def __init__(self, prev_hash, node_id):
    #self.block_hash = uuid.uuid4()
    self.block_hash = Block.counter
    Block.counter += 1
    self.prev_hash = prev_hash
    self.node_id = node_id

  def __lt__(self, other):
    return self.block_hash < other.block_hash

  def __eq__(self, other):
    return self.block_hash == other.block_hash
