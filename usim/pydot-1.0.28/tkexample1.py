#!/bin/env python2.7
# author: Michael Kimi
# date  : Fri Jan 10 15:11:41 2014


from Tkinter import *

root = Tk()

content = Frame(root)
frame = Frame(content, borderwidth=5, relief="sunken", width=200, height=100)
namelbl = Label(content, text="Name")
name = Entry(content)

onevar = BooleanVar()
twovar = BooleanVar()
threevar = BooleanVar()

onevar.set(True)
twovar.set(False)
threevar.set(True)

one = Checkbutton(content, text="One", variable=onevar, onvalue=True)
two = Checkbutton(content, text="Two", variable=twovar, onvalue=True)
three = Checkbutton(content, text="Three", variable=threevar, onvalue=True)
ok = Button(content, text="Okay")
cancel = Button(content, text="Cancel")

content.grid(column=0, row=0, sticky=(N, S, E, W))

frame.grid  (column=0, row=0, columnspan=3, rowspan=3, sticky=(N, S, E, W))
namelbl.grid(column=3, row=0, columnspan=2,            sticky=(N, W),    padx=5)
name.grid   (column=3, row=1, columnspan=2,            sticky=(N, E, W), padx=5, pady=5)
one.grid    (column=0, row=3)
two.grid    (column=1, row=3)
three.grid  (column=2, row=3)
ok.grid     (column=3, row=3)
cancel.grid (column=4, row=3)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
content.columnconfigure(0, weight=3)
content.columnconfigure(1, weight=3)
content.columnconfigure(2, weight=3)
content.columnconfigure(3, weight=1)
content.columnconfigure(4, weight=1)
content.rowconfigure(1, weight=1)

root.mainloop()
