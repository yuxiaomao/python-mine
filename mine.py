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
    self.flag_count = 0
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
    if self.arr_marks[row][col] == CellMark.Flag:
      self.flag_count -= 1
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
      self.flag_count += 1
      mtext = "F"
    elif self.arr_marks[row][col] == CellMark.Flag:
      self.arr_marks[row][col] = CellMark.Unknown
      self.flag_count -= 1
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
import time

class MyWindow:
  def __init__(self):
    # Variables
    self.gs = None # GameSpace
    self.frm_cells = None # Frame containing cells
    self.cells = [] # Array containing widget for each cell
    self.cell_left_pressed = False # Cell press state
    self.cell_right_pressed = False # Cell press state
    self.popup_root = None # PopUp with win/lose message

    # Window
    self.root = tkinter.Tk()
    self.root.title("Minesweeper - YM")
    self.root.resizable(False, False)
    self.center_window(self.root, self.root)
    self.frm_root = tkinter.Frame(self.root)
    self.frm_root.grid()

    # Gen menu
    self.menu = self.gen_menu(self.root)

    # Gen content
    self.frm_bar = tkinter.Frame(self.frm_root, padx=10)
    self.frm_bar.grid(sticky="ew")
    self.frm_bar.pack_propagate(False)
    self.frm_bar.grid_columnconfigure(0, weight=1)
    self.frm_bar.grid_columnconfigure(1, weight=1)
    # Timer
    self.timelabel = tkinter.Label(self.frm_bar)
    self.timelabel.grid(column=0, row=0, sticky="w")
    self.current_time = 0
    self.timer_job_id = None
    # Remaining mine count
    self.remaining_mine_count = tkinter.Label(self.frm_bar)
    self.remaining_mine_count.grid(column=1, row=0, sticky="e")
    # Default level
    self.start_game(9, 9, 10)

    # Mainloop
    self.root.mainloop()

  # Center window (with content) to target (default to screen)
  def center_window(self, window, content, target = None):
    # Force window generation
    content.update_idletasks()
    # Get actual size
    w = content.winfo_width()
    h = content.winfo_height()
    # Compute x and y coordinates for the Tk root window
    if target == None:
      ws = window.winfo_screenwidth() # width of the screen
      hs = window.winfo_screenheight() # height of the screen
      x = (ws/2) - (w/2)
      y = (hs/2) - (h/2)
    else:
      ws = target.winfo_width()
      hs = target.winfo_height()
      x = (ws/2) - (w/2) + target.winfo_x()
      y = (hs/2) - (h/2) + target.winfo_y()
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    print(f"[center_window] w:{w} x h:{h} x:{x} y:{y}")

  # Update window size with content size, but do not move window
  def update_window_size(self, window, content):
    # Force window generation
    content.update_idletasks()
    # Set the dimensions of the window
    w = content.winfo_width()
    h = content.winfo_height()
    window.geometry('%dx%d' % (w, h))
    print(f"[update_window_size] w:{w} x h:{h}")

  def start_timer(self):
    self.stop_timer()
    self.current_time = 0
    self.update_time(time.time())

  def stop_timer(self):
    if self.timer_job_id != None:
      self.root.after_cancel(self.timer_job_id)

  # Update time periodically, should only be called by start_timer
  def update_time(self, start_time):
    self.current_time = time.time() - start_time
    dtext = "Time: " + str(int(self.current_time))
    self.timelabel.configure(text=dtext)
    self.timer_job_id = self.root.after(100, lambda s=start_time: self.update_time(start_time))

  def update_remaining_mine_count(self):
    count = self.gs.mine_count - self.gs.flag_count
    dtext = "Remaining: " + str(count)
    self.remaining_mine_count.configure(text=dtext)

  def gen_menu(self, root):
    # Menu root
    newmenu = tkinter.Menu(root)
    root.config(menu=newmenu)
    # Menu "New Game", without leading dashed line
    cascadeMenu = tkinter.Menu(newmenu, tearoff=False)
    newmenu.add_cascade(label="New Game", menu=cascadeMenu)
    cascadeMenu.add_command(label="Beginner", command=lambda: self.start_game(9, 9, 10))
    cascadeMenu.add_command(label="Intermediate", command=lambda: self.start_game(16, 16, 40))
    cascadeMenu.add_command(label="Expert", command=lambda: self.start_game(16, 30, 99))
    cascadeMenu.add_command(label="Custom", command=lambda: self.gen_difficulty_popup())
    return newmenu

  def gen_message_popup(self, msg):
    self.popup_root = tkinter.Toplevel(self.root)
    self.popup_root.title("")
    self.popup_root.resizable(False, False)
    frame = tkinter.Frame(self.popup_root, padx=10, pady=10)
    frame.grid()
    self.center_window(self.popup_root, frame, self.root)
    tkinter.Label(frame, text=msg).grid(column=0, row=0)
    tkinter.Button(frame, text="Restart", command=lambda: self.start_game(self.gs.row, self.gs.col, self.gs.mine_count)).grid(column=0, row=1)
    self.center_window(self.popup_root, frame, self.root)

  def gen_difficulty_popup(self):
    self.popup_root = tkinter.Toplevel(self.root)
    self.popup_root.title("Custom")
    self.popup_root.resizable(False, False)
    frame = tkinter.Frame(self.popup_root, padx=10, pady=10)
    frame.grid()
    self.center_window(self.popup_root, frame, self.root)
    tkinter.Label(frame, text="Height (9-30)").grid(column=0, row=0)
    tkinter.Label(frame, text="Width (9-30)").grid(column=0, row=1)
    tkinter.Label(frame, text="Mines (>=10)").grid(column=0, row=2)
    # Force entry data type to int
    def validate_callback(P):
      if str.isdigit(P) or P == "":
        return True
      else:
        return False
    vcmd = (frame.register(validate_callback), '%P')
    entry1 = tkinter.Entry(frame, width=5, validate='all', validatecommand=vcmd)
    entry1.grid(column=1, row=0)
    entry2 = tkinter.Entry(frame, width=5, validate='all', validatecommand=vcmd)
    entry2.grid(column=1, row=1)
    entry3 = tkinter.Entry(frame, width=5, validate='all', validatecommand=vcmd)
    entry3.grid(column=1, row=2)
    # Fill default value for entry
    entry1.insert(0, str(self.gs.row))
    entry2.insert(0, str(self.gs.col))
    entry3.insert(0, str(self.gs.mine_count))
    tkinter.Button(frame, text="Start",
                   command=lambda: self.start_game(int(entry1.get()), int(entry2.get()), int(entry3.get()))
                   ).grid(column=0, row=3, columnspan = 2)
    self.center_window(self.popup_root, frame, self.root)

  def start_game(self, row, col, mine):
    if self.popup_root != None:
      self.popup_root.destroy()
    self.gen_level(row, col, mine)
    self.start_timer()

  def gen_level(self, row, col, mine):
    # Check row, col, mine_count value before generate gamespace
    if row < 9: row = 9
    if row > 30: row = 30
    if col < 9: col = 9
    if col > 30: col = 30
    if mine < 10: mine = 10
    if mine > (row*col): mine = row*col
    self.gs = GameSpace(row, col, mine)
    print(f"[gen_level] row:{row} col:{col} mine:{mine}")
    # print(self.gs) # Spoiler!!
    if self.frm_cells != None:
      self.frm_cells.grid_forget()
    self.frm_cells = tkinter.Frame(self.frm_root, padx=10, pady=10, background="white")
    self.frm_cells.grid()
    self.cells = gen_array(row, col)
    for r in range(row):
      for c in range(col):
        self.cells[r][c] = self.gen_cell(self.frm_cells, r, c)
        self.cells[r][c].grid(column=c, row=r)
    self.update_remaining_mine_count()
    self.update_window_size(self.root, self.frm_root)

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
    # Refresh display
    self.update_remaining_mine_count()

  # Reveal cell begin at (row, col), loop reveal surrounding cells if no mine around
  def reveal_cells(self, row, col):
    # List of cells to reveal
    pending_cells = [(row, col)]
    def func(r, c):
      pending_cells.append((r, c))
    while (len(pending_cells) > 0):
      (prow, pcol) = pending_cells.pop()
      if self.reveal_cell(prow, pcol):
        do_for_surrounding(self.gs.row, self.gs.col, prow, pcol, func)

  # Reveal a single cell at (row, col)
  # Should only be called by self.reveal_cells
  # Return true if revealed an empty cell (no mine around)
  def reveal_cell(self, row, col):
    revealed_empty = False
    # Do nothing if already revealed
    if self.gs.arr_marks[row][col] == CellMark.Revealed:
      return revealed_empty
    # If not revealed yet, set and check gamespace
    self.cells[row][col].configure(relief=tkinter.RIDGE)
    # Check Win/Lose state if gamestate changed after mark cell reveal
    if self.gs.mark_cell_revealed(row, col):
      self.stop_timer()
      if self.gs.state == GameState.Lose:
        self.show_all_mines()
        self.gen_message_popup("You Lose")
        print("BOOOOM!")
      elif self.gs.state == GameState.Win:
        self.gen_message_popup("You Win")
        print("Congratulations! Time: " + ('%.1f' % self.current_time))
    # Update revealed cell content, recursive reveal if cell has no mines around
    if self.gs.arr_mines[row][col]:
      self.cells[row][col].configure(text="*", fg="black")
    elif self.gs.arr_tips[row][col] > 0:
      self.cells[row][col].configure(text=str(self.gs.arr_tips[row][col]), fg="black")
    else: # self.gs.arr_tips[row][col] == 0
      self.cells[row][col].configure(text="", fg="black")
      revealed_empty = True
    return revealed_empty

  def show_all_mines(self):
    for r in range(self.gs.row):
      for c in range(self.gs.col):
        if self.gs.arr_mines[r][c]:
          self.cells[r][c].configure(text="*", fg="black")

  def mark_cell(self, row, col):
    # Do nothing if already revealed
    if self.gs.arr_marks[row][col] == CellMark.Revealed:
      return
    # If not revealed
    widget = self.cells[row][col]
    # Animate Right click
    widget.configure(relief=tkinter.SUNKEN)
    self.root.after(50, lambda: widget.configure(relief=tkinter.RAISED))
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
    else:
      # If not equal, do animation on surrounding not revealed/flag cells
      def func(r, c):
        if self.gs.arr_marks[r][c] != CellMark.Revealed and self.gs.arr_marks[r][c] != CellMark.Flag:
          self.cells[r][c].configure(relief=tkinter.SUNKEN)
          self.root.after(50, lambda: self.cells[r][c].configure(relief=tkinter.RAISED))
      do_for_surrounding(self.gs.row, self.gs.col, row, col, func)

# ----- Main -----
MyWindow()
