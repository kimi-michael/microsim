#!/bin/env python2.7
# author: Michael Kimi
# date  : Wed Dec 11 09:35:46 2013

"""defines the list widget class"""

from Tkinter import *


class AddRemoveListWidget(LabelFrame):

    def __init__(self, parent_frame, entry_list, width, height, num_display_items, add_function,
                 text):
        """ctor, will places in parent_frame, list's entries will be taken from entry_list
        widgets dimensions. number of list entries that will be displayed is num_display_items.
        add_function will be called each time ADD button is pressed. text - displayed name of
        the frame"""

        LabelFrame.__init__(self, master=parent_frame, width=width, height=height, text=text)
                       #,borderwidth=3, relief=GROOVE)

        self.get_item_to_add = add_function

        # add the list of items
        self.list_box = Listbox(self, height=num_display_items)
        for item in entry_list:
            self.list_box.insert(END, item)

        # add scroll bars
        self.list_vscroll = Scrollbar(self, orient=VERTICAL)
        self.list_hscroll = Scrollbar(self, orient=HORIZONTAL)

        # add buttons
        self.add_button = Button(self, text="Add", command=self.add_action)
        self.remove_button = Button(self, text="Remove", command=self.remove_action)
        #self.label = Label(self, text=text)

        self._bind_scrollbars()
        self._set_layout()

    def _set_layout(self):
        """place all widgets in the frame"""
        # config layout of all elements
        #self.label.grid(row=0, column=0, sticky=W, columnspan=4)
        self.list_box.grid(row=1, column=0, sticky=NSEW, columnspan=3, rowspan=2)
        self.list_vscroll.grid(row=1, column=3, sticky=NS, rowspan=2)
        self.list_hscroll.grid(row=3, column=0, sticky=EW, columnspan=3)
        self.add_button.grid(row=4, column=0, sticky=EW, padx=3, pady=4)
        self.remove_button.grid(row=4, column=2, sticky=EW, padx=3, pady=4)

        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

    def _bind_scrollbars(self):
        # bind scroll to the list
        self.list_vscroll.configure(command=self.list_box.yview)
        self.list_hscroll.configure(command=self.list_box.xview)
        self.list_box.configure(yscrollcommand=self.list_vscroll.set)
        self.list_box.configure(xscrollcommand=self.list_hscroll.set)

    def add_action(self):
        item = self.get_item_to_add()
        self.list_box.insert(END, item)

    def remove_action(self):
        index = self.which_selected()
        if index >= 0:
            self.list_box.delete(index, index)

    def which_selected(self):
        selection_list = self.list_box.curselection()
        if len(selection_list) > 0:
            return int(selection_list[0])
        else:
            return -1

    def get_items(self):
        return self.list_box.get(0, END)


if __name__ == "__main__":
    def rand():
        import random
        return random.randint(1, 100)

    win = Tk()

    frame = Frame(win)

    element_list = range(10)
    widget = AddRemoveListWidget(frame, element_list, 700, 500, 5, rand, "Random Nums")
    widget.grid(row=0, column=0, sticky=NSEW)

    win.columnconfigure(0, weight=1)
    win.rowconfigure(0, weight=1)

    frame.grid(row=0, column=0, sticky=NSEW)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    win.mainloop()
