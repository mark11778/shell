import os
import sys
import subprocess
from subprocess import Popen, PIPE
from collections import deque
from curses.ascii import isdigit


class term:
    SPECIAL_CHARS = {'=', '/', '$', '|'}

    def __init__(self, cwd):
        self.cwd = cwd
        self.built_in = None

    def varSub(self, args):
        """ go through the split up command and look for vars to be subsituted"""
        for i in range(len(args)):
            if "$" in args[i]:
                args[i] = os.environ[args[i][1:]] # remove the $

    def cd(self, args):
        """ change directory, just updates cwd attribute"""
        if len(args) == 1:
            print("Error cd takes two arguments")
            return
        if args[1] == "..":
            self.cwd = os.path.dirname(os.getcwd())
        else:
            if args[1] in os.listdir(self.cwd):
                self.cwd = os.path.join(self.cwd, args[1])

    def leave(self, args):
        """gracefully exits terminal"""
        if len(args) == 1:
            sys.exit(0)
        else:
            if args[1].isdigit():
                sys.exit(int(args[1]))
            else:
                print("Error leave takes one argument")

    def getcwd(self, args):
        """ simple getter function """
        if len(args) != 1:
            print("cwd takes only one argument")
        else:
            print(self.cwd)

    def export(self, args):
        """sets envoirment variables"""
        if len(args) == 1 or len(args) > 2:
            print("error export takes two arguements")
        else:
            if args[1]:
                var, _, val = args[1].partition("=")
                if var and val: # both are defined
                    if not (set(var) & self.SPECIAL_CHARS) and not (set(val) & self.SPECIAL_CHARS): # true when intersect is none
                        os.environ[var] = val
                    else:
                        print("error do not use special chars in name or vals of enviorment variables")

    def strt(self):
        def parse_input(cmd_full):
            # remove white space
            return cmd_full.strip().split(" ")

        def call_command(args):
            if args[0] in self.built_in:
                self.built_in[args[0]](args)
                return None
            else: return Popen(args, cwd=self.cwd, stdout=PIPE, stderr=PIPE)


        def handle_pipes(args):
            """ handling commands with pipes | :)"""
            lst = 0
            s = deque([])
            for i in range(len(args)):
                if args[i] == "|":
                    # first command
                    if lst == 0:
                        s.append(Popen(args[lst : i], cwd=self.cwd, stdout=PIPE))
                    s.append(Popen(args[lst : i], cwd=self.cwd, stdin = s.pop().stdout, stdout=PIPE))
                    lst = i + 1
            # handling the last command
            return Popen(args[lst: ], cwd=self.cwd, stdin=s.pop().stdout, stdout=PIPE)


        def print_output(p):
            assert isinstance(p, Popen)
            out, err = p.communicate()
            if err:  # true (non-zero return code)
                print(f"commnad returned an error: {err.decode("utf-8")}")
            else:
                print(out.decode("utf-8").strip())

        while True:
            res = None
            cmd = input(f"{self.cwd}:> ")
            arg = parse_input(cmd)
            #TODO: implement command subsitution
            if "$" in cmd:
                self.varSub(arg)
            if "|" in cmd:
                res = handle_pipes(arg)
            else:
                res = call_command(arg)

            if res is not None:
                print_output(res)


    def run(self):
        self.built_in = {
            "cd": self.cd,
            "exit": self.leave,
            "cwd": self.getcwd,
            "export": self.export,
        }
        self.strt()

if __name__ == "__main__":
    t = term(os.getcwd())
    t.run()

