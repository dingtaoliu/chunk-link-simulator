import uuid 

class Block:
  
  # pointer to parent block
  prev_hash = None

  # simulated block hash
  block_hash = None 

  # list of verified transactions
  transactions = []

  def __init__(self):
    self.block_hash = uuid.uuid4()
