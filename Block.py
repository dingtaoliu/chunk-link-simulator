import uuid 

class Block:
  
  # counter
  counter = 1
  def __init__(self, prev_hash):
    #self.block_hash = uuid.uuid4()
    self.block_hash = Block.counter
    Block.counter += 1
    self.prev_hash = prev_hash
