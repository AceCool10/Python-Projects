#! /usr/bin/python3
import math
import random
import tkinter
import tkinter.messagebox
from tkinter import *
game = input("How many columns do you want?   ")
game = int(game)
game_two = input("How many rows do you want?   ")
game_two = int(game)

def odd(n):
    return n & 1
def color(a):
    return 'green' if odd(a) else 'blue'
class Map:
    def __init__(self, master, rows = game_two, columns = game):
        self.master = master
        self.row = random.randrange(rows)
        self.col = random.randrange(columns)
        self.cost = 0
        self.found = False
        Button = tkinter.Button
        self.buttons = []
        options = dict(text = '--', font = 'Courier 14')
        for r in range(rows):
            br = []                 # row of buttons
            self.buttons.append(br)
            for c in range(columns):
                b = Button(
                    master,
                    command = lambda r=r, c=c: self(r, c),
                    fg = color(r+c),
                    **options
                    )
                b.grid(row = r, column = c)
                br.append(b)
        master.mainloop()
    def __bool__(self):
        return self.found
    def __call__(self, row, col):
        if self:
            self.master.quit()
        distance = int(round(math.hypot(row-self.row, col-self.col)))
        self.buttons[row][col].configure(text = '{}'.format(distance), bg = 'light grey', fg = 'black')
        self.cost += 1
        if not distance:
            print('You win!  At the cost of {} clicks.'.format(self.cost))
            self.found = True
            root_two = Tk()
            w = Label(root_two, text = "You win!  At the cost of {} clicks.".format(self.cost)).grid(row = 0, column = 1)
            w.pack()
def main():
    root = tkinter.Tk()
    map = Map(root)
    root.destroy()
if __name__ == '__main__':
    main()
