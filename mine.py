# Main file

# ----- Util -----

from enum import Enum

class CellMark(Enum):
  Revealed = -1
  NoMark = 0
  Flag = 1
  Unknown = 2

class GameState(Enum):
  InGame = 0
  Win = 1
  Lose = 2

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

# Do func on (row, col)'s surrounding inside array (max_r, max_c)
def do_for_surrounding(max_r, max_c, row, col, func, min_r = 0, min_c = 0):
  for (r, c) in (
    (row-1, col-1), (row-1, col), (row-1, col+1),
    (row,   col-1),               (row,   col+1),
    (row+1, col-1), (row+1, col), (row+1, col+1),
    ):
    if (r >= min_r and r < max_r and c >= min_c and c < max_c):
      func(r, c)

# Count presence of value in surrounding 8 cells if the current cell is not value
# Return -1 otherwise
def count_value_surrounding(array, value, max_r, max_c, row, col, min_r = 0, min_c = 0):
  count = 0
  if array[row][col] == value:
    return -1
  def func(r, c):
    nonlocal count
    if array[r][c] == value:
      count += 1
  do_for_surrounding(max_r, max_c, row, col, func)
  return count


# ----- Core -----

from random import randrange

class GameSpace:
  def __init__(self, row, col, mine_count):
    # Param variables
    self.row = row
    self.col = col
    self.mine_count = mine_count

    # Constant
    self.size = self.row * self.col
    self.empty_count = self.size - self.mine_count

    # Other variables
    self.arr_mines = self.gen_mines_position()
    self.arr_tips = self.gen_tips_array()
    self.arr_marks = [[CellMark.NoMark for x in range(self.col)] for x in range(self.row)]
    self.reveal_count = 0
    self.state = GameState.InGame

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
        tips[r][c] = count_value_surrounding(self.arr_mines, True, self.row, self.col, r, c)
    return tips

  # Mark cell at (row, col) with CellMark.Revealed
  # Hypothesis: self.state == GameState.InGame, cell not revealed
  # Return true if gamestate changed
  def mark_cell_revealed(self, row, col):
    self.arr_marks[row][col] = CellMark.Revealed
    self.reveal_count += 1
    # Check if lose or win
    gamestate_changed = False
    if self.arr_mines[row][col]:
      self.state = GameState.Lose
      gamestate_changed = True
    elif self.reveal_count == self.empty_count:
      self.state = GameState.Win
      gamestate_changed = True
    return gamestate_changed

  # Mark cell at (row, col) with next cellmark
  # Hypothesis: self.state == GameState.InGame, cell not revealed
  def mark_cell_next(self, row, col):
    if self.arr_marks[row][col] == CellMark.NoMark:
      self.arr_marks[row][col] = CellMark.Flag
      mtext = "F"
    elif self.arr_marks[row][col] == CellMark.Flag:
      self.arr_marks[row][col] = CellMark.Unknown
      mtext = "?"
    elif self.arr_marks[row][col] == CellMark.Unknown:
      self.arr_marks[row][col] = CellMark.NoMark
      mtext = ""
    return mtext

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
    self.gs = None # GameSpace
    self.frm = None # Frame containing mines
    self.cells = [] # Array containing widget for each cell
    self.cell_left_pressed = False # Cell press state
    self.cell_right_pressed = False # Cell press state
    self.popuproot = None # PopUp with win/lose message

    # Window
    self.root = tkinter.Tk()
    self.root.title("Minesweeper - by YM")
    self.root.resizable(False, False)
    # Gen menu
    self.menu = self.gen_menu(self.root)
    self.update_window(self.root, self.root)
    # Default level
    self.gen_level(self.root, 9, 9, 10)

    # Mainloop
    self.root.mainloop()

  def update_window(self, window, content):
    # Force window generation
    content.update_idletasks()
    # Get actual size
    w = content.winfo_width()
    h = content.winfo_height()
    # Compute x and y coordinates for the Tk root window
    ws = window.winfo_screenwidth() # width of the screen
    hs = window.winfo_screenheight() # height of the screen
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    # Set the dimensions and position of the window
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))
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

  def gen_popup(self, msg):
    self.popuproot = tkinter.Toplevel(self.root)
    self.popuproot.title("")
    self.popuproot.resizable(False, False)
    frame = tkinter.Frame(self.popuproot, padx=10, pady=10)
    frame.grid()
    tkinter.Label(frame, text=msg).grid(column=0, row=0)
    tkinter.Button(frame, text="Restart", command=lambda: self.game_restart()).grid(column=0, row=1)
    self.update_window(self.popuproot, frame)

  def game_restart(self):
    self.popuproot.destroy()
    self.gen_level(self.root, self.gs.row, self.gs.col, self.gs.mine_count)

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
    self.update_window(self.root, self.frm)

  def gen_cell(self, root, row, col):
    button = tkinter.Label(root, width=2, height=1, borderwidth=2, relief=tkinter.RAISED)
    button.bind("<Button-1>", lambda event, r=row, c=col: self.on_left_click_cell(event, r, c))
    button.bind("<Button-2>", lambda event, r=row, c=col: self.on_right_click_cell(event, r, c))
    button.bind("<Button-3>", lambda event, r=row, c=col: self.on_right_click_cell(event, r, c))
    return button

  def on_left_click_cell(self, event, row, col):
    self.cell_left_pressed = True
    self.root.after(50, lambda: self.on_click_cell_later(row, col))

  def on_right_click_cell(self, event, row, col):
    self.cell_right_pressed = True
    self.root.after(50, lambda: self.on_click_cell_later(row, col))

  def on_click_cell_later(self, row, col):
    if self.gs.state != GameState.InGame:
      return
    if not self.cell_right_pressed and not self.cell_left_pressed:
      return
    if self.cell_right_pressed and self.cell_left_pressed:
      # Both left and right are clicked
      self.validate_cell(row, col)
    elif self.cell_left_pressed:
      # Only left is clicked
      self.reveal_cells(row, col)
    elif self.cell_right_pressed:
      # Only right is clicked
      self.mark_cell(row, col)
    # Reset press state
    self.cell_left_pressed = False
    self.cell_right_pressed = False

  def reveal_cells(self, row, col):
    # Do nothing if already revealed
    if self.gs.arr_marks[row][col] == CellMark.Revealed:
      return
    # If not revealed yet, set and check gamespace
    self.cells[row][col].configure(relief=tkinter.RIDGE)
    # Show Win/Lose message if gamestate changed after reveal cell
    if self.gs.mark_cell_revealed(row, col):
      if self.gs.state == GameState.Lose:
        self.gen_popup("You Lose")
      elif self.gs.state == GameState.Win:
        self.gen_popup("You Win")
    # Update revealed cell content, recursive reveal if cell has no mines around
    if self.gs.arr_mines[row][col]:
      self.cells[row][col].configure(text="*", fg="black")
      print("BOOOOM!")
    elif self.gs.arr_tips[row][col] > 0:
      self.cells[row][col].configure(text=str(self.gs.arr_tips[row][col]), fg="black")
    else: # self.gs.arr_tips[row][col] == 0
      # Reveal all surrounding cells because they are safe
      do_for_surrounding(self.gs.row, self.gs.col, row, col, lambda r, c: self.reveal_cells(r, c))

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
    marktext = self.gs.mark_cell_next(row, col)
    widget.configure(text=marktext, fg="red")

  def validate_cell(self, row, col):
    # If not reveal, reveal
    if self.gs.arr_marks[row][col] != CellMark.Revealed:
      self.reveal_cells(row, col)
      return
    # Count surrounding flags
    count = 0
    def func(r, c):
      nonlocal count
      if self.gs.arr_marks[r][c] == CellMark.Flag:
        count += 1
    do_for_surrounding(self.gs.row, self.gs.col, row, col, func)
    # Reveal surrounding no flag cells if count equal to tips
    if count == self.gs.arr_tips[row][col]:
      def func(r, c):
        if self.gs.arr_marks[r][c] != CellMark.Flag:
          self.reveal_cells(r, c)
      do_for_surrounding(self.gs.row, self.gs.col, row, col, func)

# ----- Main -----
MyWindow()
