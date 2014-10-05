#!/bin/env python2.7
# author: Michael Kimi
# date  : Wed Dec 25 2013

from Tkinter import *
from config_widget import ConfigWidget
from design_viewer import DesignViewer
import tkMessageBox as msgBox
import microSim as mSim
import threading
import shlex
import os

LOGO_FILE_NAME = 'usim_logo.gif'

class SimulatorThread(threading.Thread):
    """thread that runs the microsim main"""
    def __init__(self, command_line):
        threading.Thread.__init__(self)
        self.command_line = command_line

    def run(self):
        mSim.main(self.command_line)

    def getMessage(self, block=True, timeout=None):
        return mSim.getMessage(block, timeout)


class MicroSimGui():
    """main application, it will run microSim's gui"""
    def __init__(self):
        self.sim_thread = None

        # create widgets
        self.root = Tk()
        self.main_frame = Frame(self.root)
        
        self.config_wg = ConfigWidget(self.main_frame, 1000, 700)
        self.run_button = Button(self.main_frame, text="Run", command=self.run_click_handler)
        self.stop_button = Button(self.main_frame, text="Stop")

        logoPath = "%s/gui/%s" % (os.environ['USIM_ROOT'] , LOGO_FILE_NAME)

        self.desing_frame = DesignViewer(self.main_frame, logoPath, borderwidth=3, relief="sunken")

        self._place_widgets()
        return

    
    def run(self):
        mainloop()

    def _place_widgets(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.main_frame.grid(row=0, column=0, sticky=NSEW)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=2)
        self.main_frame.columnconfigure(3, weight=2)
        self.main_frame.rowconfigure(0, weight=1)

        options = dict(padx=3, pady=4)
        self.config_wg.grid(row=0, column=0, columnspan=2, sticky=NSEW)
        self.run_button.grid(row=1, column=0, sticky=W, **options)
        self.stop_button.grid(row=1, column=1, sticky=E, **options)

        self.desing_frame.grid(row=0, column=2, columnspan=2, rowspan=2, sticky=NSEW)

        return

    def run_click_handler(self):
        """Implements the actions when run button is clicked"""
        if self.validate_exec_fields() is not 0 or self.validate_run_fields() is not 0:
            return
        self.modify_search_path()
        command_line = self.build_microsim_exec_command()
        invoke_command = "microSim %s" % command_line
        print "Info: invocation command:", invoke_command
        
        self.sim_thread = SimulatorThread(shlex.split(invoke_command))
        self.sim_thread.run()  # run simulator's thread

        msg_type, msg = self.sim_thread.getMessage(block=True, timeout=5)
        if msg_type == 'design_pic_update' :
            self.desing_frame.load_image(msg)
        

    def validate_exec_fields(self):
        error_count = 0

        if len(self.config_wg.get_modules_list()) == 0:
            error_count += 1
            msgBox.showerror("Incorrect value", "Please fill at least one module")

        if self.config_wg.get_top() is None or self.config_wg.get_top() is "":
            error_count += 1
            msgBox.showerror("Incorrect value", "Top module should be non empty")

        if self.config_wg.get_test() is None or self.config_wg.get_test() is "":
            error_count += 1
            msgBox.showerror("Incorrect value", "Test name should be non empty")

        return error_count

    def validate_run_fields(self):
        run_mode = self.config_wg.get_run_mode()
        return 0

    def build_microsim_exec_command(self):
        exec_command = ''
        for module_name in self.config_wg.get_modules_list():
            exec_command += '--module %s ' % module_name

        exec_command += '--top %s ' % self.config_wg.get_top()
        exec_command += '--test %s ' % self.config_wg.get_test()
        exec_command += self.config_wg.get_run_mode().toCommand()
        if self.config_wg.get_resolve_zero_time():
            exec_command += '--resolveZeroTime '
        return exec_command

    def modify_search_path(self):
        """append paths appearing in GUI to python search path, if they aren't already exits in python path"""
        path_list = os.environ['PYTHONPATH'].split(":")

        #find paths which doesn't exit in python path
        for path in self.config_wg.get_search_path_list():
            if path in path_list:
                continue
            # add missing paths
            if len(os.environ['PYTHONPATH']) > 0:
                os.environ['PYTHONPATH'] += ':%s' % path
            else:
                os.environ['PYTHONPATH'] = path



if __name__ == "__main__":
    gui = MicroSimGui()
    gui.run()
