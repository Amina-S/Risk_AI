from player import Player

class State():
  def __init__(self, current_player, opponent, move=None, h=0,  children=[], likelihood=0, trp_terr=[], opp_trp_terr=[]):
    self.current_player = current_player
    self.opponent = opponent
    self.move = move
    # self.parent = parent
    self.children = children
    self.likelihood = likelihood
    self.trp_terr = trp_terr
    self.opp_trp_terr = opp_trp_terr
    self.h = h

  def add_child(self, s):
    self.children.append(s) 

  def get_children(self):
    return self.children


  def get_likelihood(self):
    return self.likelihood 

  def set_h(self, h):
    self.h = h

  def get_h(self):
    return self.h


  def get_opp_trp_terr(self):
    return self.opp_trp_terr
  

  def get_trp_terr(self):
    return self.trp_terr
  

  def set_opp_trp_terr(self, ott):
    self.opp_trp_terr = ott
  

  def set_trp_terr(self, tt):
    self.trp_terr = tt
  
  def get_troops(self, t_id):
    for (t, num) in self.trp_terr+self.opp_trp_terr:
      if (t==t_id):
        return num
    raise Exception('Given id is not found')
    
  def get_current_player(self):
    assert type(self.current_player) is Player
    return self.current_player
  
  def get_opponent(self):
    assert type(self.opponent) is Player
    return self.opponent

  def get_move(self):
    return self.move


