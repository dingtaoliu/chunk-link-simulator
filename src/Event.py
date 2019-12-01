from enum import Enum

class EventType(Enum):
  CREATE_BLOCK = 1
  RECEIVE_BLOCK = 2
  
class Event:
  def __init__(self, event, block, timestamp):
    self.event_type = event
    self.block = block
    self.timestamp = timestamp

  def __lt__(self, other):
    if self.timestamp == other.timestamp:
      return self.block.block_hash < other.block.block_hash
    return self.timestamp < other.timestamp

  def __eq__(self, other):
    return self.timestamp == other.timestamp
