#!/bin/env python2.7
# author: Michael Kimi
# date  : Wed Dec 25 2013

from Tkinter import *
from add_remove_list_widget import AddRemoveListWidget
import tkMessageBox
from tkFileDialog import *
from run_mode import RunMode, RUN_MODE


class ConfigWidget(Frame):

    def __init__(self, parent_frame, width, height):
        Frame.__init__(self, master=parent_frame, width=width, height=height)

        top_label = Label(self, text="top")
        test_label = Label(self, text="test")

        # bound variables
        self.top_string = StringVar()
        self.test_string = StringVar()
        self.run_mode = IntVar()
        self.run_until_tick_str = StringVar()
        self.run_until_event_str = StringVar()
        self.is_resolve_zero = IntVar()

        val_num_cmd = (self.register(self.validate_number), '%S')
        val_str_cmd = (self.register(self.validate_string), '%S')

        # gui interactive elements:
        self.search_path_wg = AddRemoveListWidget(self, [], 800, 300, 4, lambda: askdirectory(title="choose directory"),
                                                  "1. Choose search path:")
        self.module_wg = AddRemoveListWidget(self, [], 500, 800, 4,
                                             lambda: ConfigWidget.get_module_name(askopenfilename(title="choose file")),
                                             "2. Choose modules:")
        run_forever_button = Radiobutton(self, text="run forever", value=0, variable=self.run_mode)
        run_until_tick_button = Radiobutton(self, text="run until tick", value=1, variable=self.run_mode)
        run_until_event_button = Radiobutton(self, text="run until event number", value=2, variable=self.run_mode)
        resolve_zero_button = Checkbutton(self, text="enable resolve zero time", variable=self.is_resolve_zero)

        run_until_tick_entry = Entry(self, textvariable=self.run_until_tick_str, validate="key",
                                     validatecommand=val_num_cmd)
        run_until_event_entry = Entry(self, textvariable=self.run_until_event_str, validate="key",
                                      validatecommand=val_num_cmd)
        top_entry = Entry(self, textvariable=self.top_string, validate="key", validatecommand=val_str_cmd)
        test_entry = Entry(self, textvariable=self.test_string, validate="key", validatecommand=val_str_cmd)

        # set the layout
        self.search_path_wg.grid(row=0, column=0, columnspan=3, sticky=NSEW)
        self.module_wg.grid(row=2, column=0, columnspan=3, sticky=NSEW)

        top_label.grid(row=3, column=0, sticky=W)
        top_entry.grid(row=3, column=1, columnspan=2, sticky=EW)

        test_label.grid(row=4, column=0, sticky=W)
        test_entry.grid(row=4, column=1, columnspan=2, sticky=EW)

        run_forever_button.grid(row=7, column=0, sticky=W)

        run_until_tick_button.grid(row=8, column=0, sticky=W)
        run_until_tick_entry.grid(row=8, column=1, columnspan=2, sticky=EW)

        run_until_event_button.grid(row=9, column=0, sticky=W)
        run_until_event_entry.grid(row=9, column=1, columnspan=2, sticky=EW)

        resolve_zero_button.grid(row=10, column=0, sticky=W)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        return

    def validate_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            tkMessageBox.showerror("Incorrect value", "Expecting number not [%s]" % s)
            return False

    def validate_string(self, s):
        if s is not "":
            return True
        else:
            tkMessageBox.showerror("Incorrect value", "Must be non empty string")
            return False

    @staticmethod
    def get_module_name(file_name):
        if file_name is None or file_name is "":
            return None
        file_with_extension = file_name.split("/")[-1]
        return file_with_extension.join(file_with_extension.split('.')[:-1])

    def get_search_path_list(self):
        return self.search_path_wg.get_items()

    def get_modules_list(self):
        return self.module_wg.get_items()

    def get_top(self):
        return self.top_string.get()

    def get_test(self):
        return self.test_string.get()

    def get_run_mode(self):
        res = RunMode()
        until = 0
        if self.run_mode.get() == 0:
            res.set_run_mode(RUN_MODE.forever)
        elif self.run_mode.get() == 1:
            res.set_run_mode(RUN_MODE.until_tick)
            if self.run_until_tick_str.get() is not "":
                until = int(self.run_until_tick_str.get())
                self.run_until_tick_str.set(until)
            res.set_until(until)
        else:
            res.set_run_mode(RUN_MODE.until_event)
            if self.run_until_event_str.get() is not "":
                until = int(self.run_until_event_str.get())
                self.run_until_event_str.set(until)
            res.set_until(until)
        return res

    def get_resolve_zero_time(self):
        return self.is_resolve_zero.get()
if __name__ == "__main__":

    win = Tk()
    frame = Frame(win)
    config_wg = ConfigWidget(frame, 600, 1000)

    win.columnconfigure(0, weight=1)
    win.rowconfigure(0, weight=1)

    frame.grid(row=0, column=0, sticky=NSEW)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    config_wg.grid(sticky=NSEW)

    mainloop()
