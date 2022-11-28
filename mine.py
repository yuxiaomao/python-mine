# Main file

# ----- Util -----
from enum import Enum

class CellMark(Enum):
    Revealed = -1
    NoMark = 0
    Flag = 1
    Unknown = 2

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
import time

class MyWindow:
  def __init__(self):
    # Variables
    self.gs = None # GameSpace
    self.frm = None # Frame containing mines
    self.cells = [] # Array containing widget for each cell

    # Window
    self.root = tkinter.Tk()
    self.root.title("Minesweeper - by YM")
    # Gen menu
    self.menu = self.gen_menu(self.root)
    self.update_window(self.root)
    # Default level
    self.gen_level(self.root, 9, 9, 10)

    # Mainloop
    self.root.mainloop()

  def update_window(self, content):
    # Force window generation
    content.update_idletasks()
    # Get actual size
    w = content.winfo_width()
    h = content.winfo_height()
    # Compute x and y coordinates for the Tk root window
    ws = self.root.winfo_screenwidth() # width of the screen
    hs = self.root.winfo_screenheight() # height of the screen
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    # Set the dimensions and position of the window
    self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    print(f"[update_window] w:{w} x h:{h}")

  def gen_menu(self, root):
    # Menu root
    newmenu = tkinter.Menu(root)
    root.config(menu=newmenu)
    # Menu "New Game", without leading dashed line
    cascadeMenu = tkinter.Menu(newmenu, tearoff=False)
    newmenu.add_cascade(label="New Game", menu=cascadeMenu)
    cascadeMenu.add_command(label="Beginner", command=lambda: self.gen_level(root, 9, 9, 10))
    cascadeMenu.add_command(label="Intermediate", command=lambda: self.gen_level(root, 16, 16, 40))
    cascadeMenu.add_command(label="Expert", command=lambda: self.gen_level(root, 16, 30, 99))
    return newmenu

  def gen_level(self, root, row, col, mine):
    self.gs = GameSpace(row, col, mine)
    print(f"[gen_level]\n{self.gs}")
    if self.frm != None:
      self.frm.grid_forget()
    self.frm = tkinter.Frame(root, padx=10, pady=10, background="white")
    self.frm.grid()
    self.cells = gen_array(row, col)
    for r in range(row):
      for c in range(col):
        self.cells[r][c] = self.gen_cell(self.frm, r, c)
        self.cells[r][c].grid(column=c, row=r)
    self.update_window(self.frm)

  def gen_cell(self, root, row, col):
    button = tkinter.Label(root, width=2, height=1, borderwidth=2, relief=tkinter.RAISED)
    button.bind("<Button-1>", lambda event, r=row, c=col: self.on_left_click_cell(event, r, c))
    button.bind("<Button-2>", lambda event, r=row, c=col: self.on_right_click_cell(event, r, c))
    button.bind("<Button-3>", lambda event, r=row, c=col: self.on_right_click_cell(event, r, c))
    return button

  def on_left_click_cell(self, event, row, col):
    self.reveal_cells(row, col)

  def on_right_click_cell(self, event, row, col):
    self.mark_cell(row, col)

  def reveal_cells(self, row, col):
    # Do nothing if already revealed
    if self.gs.arr_marks[row][col] == CellMark.Revealed:
      return
    # If not revealed yet, set and check gamespace
    self.gs.arr_marks[row][col] = CellMark.Revealed
    self.cells[row][col].configure(relief=tkinter.RIDGE)
    if self.gs.arr_mines[row][col]:
      self.cells[row][col].configure(text="*", fg="black")
      print("BOOOOM!")
    elif self.gs.arr_tips[row][col] > 0:
      self.cells[row][col].configure(text=str(self.gs.arr_tips[row][col]), fg="black")
    else: # self.gs.arr_tips[row][col] == 0
      # Reveal all surrounding cells because they are safe
      for (r, c) in (
        (row-1, col-1), (row-1, col), (row-1, col+1),
        (row,   col-1),               (row,   col+1),
        (row+1, col-1), (row+1, col), (row+1, col+1),
        ):
        if (r >= 0 and r < self.gs.row and c >= 0 and c < self.gs.col):
          self.reveal_cells(r, c)

  def mark_cell(self, row, col):
    # Do nothing if already revealed
    if self.gs.arr_marks[row][col] == CellMark.Revealed:
      return
    # If not revealed
    widget = self.cells[row][col]
    # Animate Right click
    widget.configure(relief=tkinter.SUNKEN)
    widget.after(50, lambda: widget.configure(relief=tkinter.RAISED))
    # Switch to next cellmark
    if self.gs.arr_marks[row][col] == CellMark.NoMark:
      self.gs.arr_marks[row][col] = CellMark.Flag
      widget.configure(text="F", fg="red")
    elif self.gs.arr_marks[row][col] == CellMark.Flag:
      self.gs.arr_marks[row][col] = CellMark.Unknown
      widget.configure(text="?", fg="red")
    elif self.gs.arr_marks[row][col] == CellMark.Unknown:
      self.gs.arr_marks[row][col] = CellMark.NoMark
      widget.configure(text="", fg="red")

# ----- Main -----
MyWindow()
