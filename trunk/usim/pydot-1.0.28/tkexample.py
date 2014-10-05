#!/bin/env python2.7
# author: Michael Kimi
# date  : Fri Jan 10 14:39:57 2014


from Tkinter import *
root = Tk()

Grid.rowconfigure(root,0,weight=1)
Grid.columnconfigure(root,0,weight=1)

frame=Frame(root)
frame.grid(row=0,column=0,sticky=N+S+E+W)

#example values
for x in range(6):
    for y in range(3):
        btn = Button(frame)
        btn.grid(column=x, row=y, sticky=NSEW)
for x in range(6):
  Grid.columnconfigure(frame,x,weight=1)
for y in range(3):
  Grid.rowconfigure(frame,y,weight=1)

root.mainloop()
