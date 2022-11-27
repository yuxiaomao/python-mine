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
def count_value_surrounding(array, value, pos_l, pos_c, max_l, max_c):
  null
  # TODO


# ----- Core -----

from random import randrange

# Generate an array with positions of mines mark as true
# Hypothesis: 0 <= mine_count <= size
def gen_mines_position(line, col, mine_count):
  size = line * col
  list_mines = [False] * size
  remaining_mines = mine_count
  while remaining_mines > 0:
    pos = randrange(size)
    if not list_mines[pos]:
      list_mines[pos] = True
      remaining_mines -= 1
  return gen_array_from_list(list_mines, col)

# Generate an array with count of surrounding mines in empty slot
# Values: 0-8 = count, 9 = is mine
def compute_tips_array(line, col, arr_mines):
  tips = gen_array(line, col)
  # TODO
  return tips

def gen_gamespace(line, col, mine_count):
  g_mines = gen_mines_position(line, col, mine_count)

# ----- Interface -----



# ----- Main -----
print(gen_mines_position(3,4,7))
