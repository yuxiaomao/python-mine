# Main file

# ----- Gamestate -----
from enum import Enum

class CellMark(Enum):
    NoMark = 0
    Flag = 1
    Unknown = 2

# ----- Util -----

# Genarate an empty array (list of list, size line * col)
def gen_array(line, col):
  my_array = []
  for x in range(line):
    my_col = [0] * col
    my_array.append(my_col)
  return my_array

# Break a list into array (list of list, size of internal list as col)
def gen_array_from_list(my_list, col):
  my_array = []
  for x in range(0, len(my_list), col):
    my_col = my_list[x: col+x]
    my_array.append(my_col)
  return my_array

# Count presence of value in surrounding 8 cells
# With array (line*col) and central position (pos_l*pos_c)
def count_value_surrounding(array, line, col, value, pos_l, pos_c, min_l = 0, min_c = 0):
  count = 0
  for (l, c) in (
    (pos_l-1, pos_c-1), (pos_l-1, pos_c), (pos_l-1, pos_c+1),
    (pos_l,   pos_c-1),                   (pos_l,   pos_c+1),
    (pos_l+1, pos_c-1), (pos_l+1, pos_c), (pos_l+1, pos_c+1),
    ):
    if (l >= min_l and l < line and c >= min_c and c < col and array[l][c] == value):
      count += 1
  return count


# ----- Core -----

from random import randrange

class GameSpace:
  def __init__(self, line, col, mine_count):
    # Param variables
    self.line = line
    self.col = col
    self.mine_count = mine_count

    # Other variables
    self.size = self.line * self.col
    self.arr_mines = self.gen_mines_position()
    self.arr_tips = self.gen_tips_array()

  # Generate an array with positions of mines mark as true
  # Hypothesis: 0 <= mine_count <= size
  def gen_mines_position(self):
    list_mines = [False] * self.size
    remaining_mines = self.mine_count
    while remaining_mines > 0:
      pos = randrange(self.size)
      if not list_mines[pos]:
        list_mines[pos] = True
        remaining_mines -= 1
    return gen_array_from_list(list_mines, self.col)

  # Generate an array with count of surrounding mines in empty slot
  # Values: 0-8 = count, 9 = is mine
  def gen_tips_array(self):
    tips = gen_array(self.line, self.col)
    for l in range(self.line):
      for c in range(self.col):
        tips[l][c] = count_value_surrounding(self.arr_mines, self.line, self.col, True, l, c)
    return tips

  # Print
  def __str__(self):
    s = ""
    for l in range(self.line):
      for c in range(self.col):
        if self.arr_mines[l][c]:
          s += "*"
        else:
          s += str(self.arr_tips[l][c])
      if l < self.line - 1:
        s += "\n"
    return s

# ----- Interface -----



# ----- Main -----
gs = GameSpace(3, 4, 7)
print(gs)
