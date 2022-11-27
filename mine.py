# Main file

# ----- Gamestate -----
from enum import Enum

class CellMark(Enum):
    Revealed = -1
    NoMark = 0
    Flag = 1
    Unknown = 2

# ----- Util -----

# Genarate an empty array (list of list, size row * col)
def gen_array(row, col):
  my_array = []
  for x in range(row):
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

# Count presence of value in surrounding 8 cells if the current cell is not value
# Return -1 otherwise
# With array (row*col) and central position (pos_l*pos_c)
def count_value_surrounding(array, row, col, value, pos_r, pos_c, min_r = 0, min_c = 0):
  count = 0
  if array[pos_r][pos_c] == value:
    return -1
  for (r, c) in (
    (pos_r-1, pos_c-1), (pos_r-1, pos_c), (pos_r-1, pos_c+1),
    (pos_r,   pos_c-1),                   (pos_r,   pos_c+1),
    (pos_r+1, pos_c-1), (pos_r+1, pos_c), (pos_r+1, pos_c+1),
    ):
    if (r >= min_r and r < row and c >= min_c and c < col and array[r][c] == value):
      count += 1
  return count

# ----- Core -----

from random import randrange

class GameSpace:
  def __init__(self, row, col, mine_count):
    # Param variables
    self.row = row
    self.col = col
    self.mine_count = mine_count

    # Other variables
    self.size = self.row * self.col
    self.arr_mines = self.gen_mines_position()
    self.arr_tips = self.gen_tips_array()
    self.arr_marks = [[CellMark.NoMark for x in range(self.col)] for x in range(self.row)]

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
    tips = gen_array(self.row, self.col)
    for r in range(self.row):
      for c in range(self.col):
        tips[r][c] = count_value_surrounding(self.arr_mines, self.row, self.col, True, r, c)
    return tips

  # Print
  def __str__(self):
    s = ""
    for r in range(self.row):
      for c in range(self.col):
        if self.arr_mines[r][c]:
          s += "*"
        else:
          s += str(self.arr_tips[r][c])
      if r < self.row - 1:
        s += "\n"
    return s

# ----- Interface -----

import tkinter

class MyWindow:
  def __init__(self):
    # Variables
    self.gs = GameSpace(3, 4, 7)
    print(self.gs)

    # Window
    self.root = tkinter.Tk()
    self.root.title("Minesweeper - by YM")
    # Center the window
    w = 400
    h = 150
    ws = self.root.winfo_screenwidth() # width of the screen
    hs = self.root.winfo_screenheight() # height of the screen
    # Calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    # Set the dimensions and position of the window
    self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    # Content
    self.frm = tkinter.Frame(self.root, padx=10, pady=10, background="white")
    self.frm.grid()
    for r in range(self.gs.row):
      for c in range(self.gs.col):
        btn = self.gen_cell(self.frm, r, c)
        btn.grid(column=c, row=r)

    # Mainloop
    self.root.mainloop()

  def gen_cell(self, root, row, col):
    button = tkinter.Label(root, width=2, height=1, borderwidth=2, relief=tkinter.RAISED)
    button.bind("<Button-1>", lambda event, r=row, c=col: self.left_click_cell(event, r, c))
    button.bind("<Button-2>", lambda event, r=row, c=col: self.right_click_cell(event, r, c))
    button.bind("<Button-3>", lambda event, r=row, c=col: self.right_click_cell(event, r, c))
    return button

  def left_click_cell(self, event, row, col):
    event.widget.configure(relief=tkinter.RIDGE)
    # Do nothing if already revealed
    if self.gs.arr_marks[row][col] == CellMark.Revealed:
      return
    # If not revealed yet, set and check gamespace
    self.gs.arr_marks[row][col] = CellMark.Revealed
    if self.gs.arr_mines[row][col]:
      event.widget.configure(text="*")
      print("BOOOOM!")
    else:
      event.widget.configure(text=str(self.gs.arr_tips[row][col]))

  def right_click_cell(self, event, row, col):
    # Do nothing if already revealed
    if self.gs.arr_marks[row][col] == CellMark.Revealed:
      return
    # Animate Right click
    event.widget.configure(relief=tkinter.SUNKEN)
    event.widget.after(50, lambda: event.widget.configure(relief=tkinter.RAISED))
    # Switch to next cellmark
    if self.gs.arr_marks[row][col] == CellMark.NoMark:
      self.gs.arr_marks[row][col] = CellMark.Flag
      event.widget.configure(text="F")
    elif self.gs.arr_marks[row][col] == CellMark.Flag:
      self.gs.arr_marks[row][col] = CellMark.Unknown
      event.widget.configure(text="?")
    elif self.gs.arr_marks[row][col] == CellMark.Unknown:
      self.gs.arr_marks[row][col] = CellMark.NoMark
      event.widget.configure(text="")

# ----- Main -----
MyWindow()
