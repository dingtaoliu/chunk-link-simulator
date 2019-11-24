import uuid 

class Block:
  
  # counter
  counter = 1

  # average block gen rate per minute
  AVG_GEN_TIME = 0.1

  METHOD = "longest_chain"

  def __init__(self, prev_hash):
    #self.block_hash = uuid.uuid4()
    self.block_hash = Block.counter
    Block.counter += 1
    self.prev_hash = prev_hash

  def __lt__(self, other):
    return self.block_hash < other.block_hash

  def __eq__(self, other):
    return self.block_hash == other.block_hash
