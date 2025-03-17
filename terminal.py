import os
import sys
import subprocess
from subprocess import Popen, PIPE
from collections import deque
from curses.ascii import isdigit


class term:
    SPECIAL_CHARS = set(['=', '/', '$', '|'])

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
        def parse_input(cmd):
            # remove white space
            cmd = cmd.strip()
            return cmd.split(" ")

        def call_command(args):
            if args[0] in self.built_in:
                self.built_in[args[0]](args)
            else:
                p = subprocess.Popen(args, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                if err: # true (non-zero return code)
                    print(f"commnad returned an error: {err.decode("utf-8")}")
                else:
                    print(out.decode("utf-8"))

        def handle_pipes(args):
            """ for pipes to work we need to take the output of the funciton of the left and input it to the function on
            the right

            thus, we need ls | grep .py, to only return the files that would have .py in the string (technically .ipynb
            would also be a match)
            """
            lst = 0
            s = deque([])
            for i in range(len(args)):
                if args[i] == "|":
                    # now everything to the left is the first command
                    # first command
                    if lst == 0:
                        s.append(Popen(args[lst : i], cwd=self.cwd, stdout=PIPE))

                    s.append(Popen(args[lst : i], cwd=self.cwd, stdin = s.pop().stdout, stdout=PIPE))

                    # # last command
                    # if i == len(args) - 1:
                    #     p2 = Popen(args[lst + 1 :], cwd=self.cwd, stdout=PIPE)


                    lst = i + 1

            # we have to do it one more time command does not end in "|"
            p = Popen(args[lst: ], cwd=self.cwd, stdin=s.pop().stdout, stdout=PIPE)
            out, err = p.communicate()
            if err:  # true (non-zero return code)
                print(f"commnad returned an error: {err.decode("utf-8")}")
            else:
                print(out.decode("utf-8"))


        while True:
            cmd = input(f"{self.cwd}:> ")
            arg = parse_input(cmd)
            #TODO: implement command subsitution
            if "$" in cmd:
                self.varSub(arg)
            if "|" in cmd:
                handle_pipes(arg)
                continue

            call_command(arg)


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

