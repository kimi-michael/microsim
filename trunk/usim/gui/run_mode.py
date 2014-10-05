from utils import Enum

RUN_MODE = Enum(['forever', 'until_tick', 'until_event'])


class RunMode(object):
    def __init__(self):
        self.run_mode = RUN_MODE.forever
        self.until = None
        return

    def set_run_mode(self, mode):
        self.run_mode = mode

    def set_until(self, until):
        self.until = until

    def get_run_mode(self):
        return self.run_mode

    def get_until(self):
        return self.until

    def toCommand(self):
        if self.run_mode == RUN_MODE.forever:
            return '-f '
        elif self.run_mode == RUN_MODE.until_tick:
            return '-u %s ' % self.until
        else:
            return '-n %s ' % self.until

    def toString(self):
        if self.run_mode == RUN_MODE.forever:
            return str(RUN_MODE.forever)
        else:
            return str(self.run_mode) + ' ' + str(self.until)

    @staticmethod
    def fromString(run_mode_string):
        full_error = "expected format: 'forever' or 'until_tick <number>' or 'until_event <number>' given '%s'"
        if run_mode_string is None or run_mode_string is "":
            raise Exception(full_error % run_mode_string)

        run_mode_list = run_mode_string.split()
        if len(run_mode_list) == 0:
            raise Exception(full_error % run_mode_string)

        run_mode_res = RunMode()
        if run_mode_list[0] == 'forever':
            run_mode_res.run_mode = RUN_MODE.forever
        elif run_mode_list[0] == 'until_tick':
            run_mode_res.run_mode = RUN_MODE.until_tick
        elif run_mode_list[0] == 'until_event':
            run_mode_res.run_mode = RUN_MODE.until_event
        else:
            raise Exception(full_error % run_mode_string)

        #todo continue parsing from here



