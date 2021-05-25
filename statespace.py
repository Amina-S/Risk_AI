class Statespace():
  def __init__(self, pointer=None):
    self.pointer = None 
  
  def set_pointer(self, init_state):
    self.pointer = init_state

  def get_pointer(self):
    return self.pointer