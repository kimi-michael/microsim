#!/bin/env python2.7
# author: Michael Kimi
# date  : Mon Jan 13 20:03:41 2014

"""defines a design viewer widget"""

from Tkinter import *


class DesignViewer(Frame):

    def __init__(self, parent_frame, file_name, **options):
        """create a design view object
        
        Arguments:
         - `parent_frame`: reference to parent widget
         - `file_name`: file name of gif image
        """
        Frame.__init__(self, master=parent_frame, **options)
        self.file_name = file_name
        self.image = None
        self.label = Label(self)
        
        self.load_image(file_name)

        self._place_widgets()
        #TODO add scroll bars late, like here: 
        # http://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-grid-of-widgets-in-tkinter

        #self.list_vscroll = Scrollbar(self, orient=VERTICAL)
        #self.list_hscroll = Scrollbar(self, orient=HORIZONTAL)
        #self._bind_scrollbars()
        
    def load_image(self, file_name):
        self.file_name = file_name
        self.image = PhotoImage(file=file_name)
        self.label.configure(image=self.image)
        
    def _place_widgets(self):
        self.label.grid(row=0, column=0, sticky=NSEW)
        #self.list_vscroll.grid(row=0, column=1, sticky=NS)
        #self.list_hscroll.grid(row=1, column=0, sticky=EW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
#    def _bind_scrollbars(self):
#        self.list_vscroll.configure(command=self.list_box.yview)
#        self.list_hscroll.configure(command=self.list_box.xview)
#        self.list_box.configure(yscrollcommand=self.list_vscroll.set)
#        self.list_box.configure(xscrollcommand=self.list_hscroll.set)
 

if __name__ == '__main__':
    image_file_name = "usim_logo.gif"

    root = Tk()  # initialize Tkinter
    dv = DesignViewer(root, image_file_name)
    
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    dv.grid(row=0, column=0, sticky=NSEW)
    dv.columnconfigure(0, weight=1)
    dv.rowconfigure(0, weight=1)

    root.mainloop()  # start the GUI
