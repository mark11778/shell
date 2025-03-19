import os
import sys
import subprocess
from subprocess import Popen, PIPE
from collections import deque

class Term:
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
            """ convert string to args (thus also argv)"""
            return cmd_full.strip().split(" ")

        def call_command(args):
            """
            finds command weather built in or not

            returns:
                Popen: if the method is not built in
            """
            if args[0] in self.built_in:
                self.built_in[args[0]](args)
                return None
            else: return Popen(args, cwd=self.cwd, stdout=PIPE, stderr=PIPE)


        def handle_pipes(args):
            """
            handling commands with pipes | :)

            returns:
                Popen: of last command
            """
            lst = 0
            s = deque([], maxlen=1)
            for i in range(len(args)):
                if args[i] == "|":
                    # first command
                    if lst == 0:
                        s.append(Popen(args[lst : i], cwd=self.cwd, stdout=PIPE, stderr=PIPE))
                    s.append(Popen(args[lst : i], cwd=self.cwd, stdin = s.pop().stdout, stdout=PIPE, stderr=PIPE))
                    lst = i + 1
            # handling the last command
            return Popen(args[lst: ], cwd=self.cwd, stdin=s.pop().stdout, stdout=PIPE, stderr=PIPE)

        def handle_command_sub(args):
            """ handling subsituting commands that are of the context $(...) """
            sub_cmd = None
            for i in range(len(args)):
                if args[i].startswith("$("):
                    args[i] = args[i][2:]
                    # need to find the matching parenthesses
                    for j in range(len(args)-1, i-1, -1):
                        if args[j].endswith(")"):
                            args[j] = args[j][:-1]
                            sub_cmd = " ".join(args[i:j+1])
                            del args[i:j + 1]
                            break
                    if sub_cmd is None:
                        print("error could not find matching parenthesis for command sub")
                        return None
                    break

            sub_out, sub_err = parse_cmd(sub_cmd).communicate()
            args.insert(i, sub_out.decode("utf-8").strip())
            return Popen(args, cwd=self.cwd, stdout=PIPE, stderr=PIPE)

        def parse_cmd(cmd):
            arg = parse_input(cmd)
            if "$(" in cmd:
                handle_command_sub(arg)
            if "$" in cmd:
                self.varSub(arg)
            if "|" in cmd:
                res = handle_pipes(arg)
            else:
                res = call_command(arg)

            return res

        def print_output(p):
            """handles out of the command"""
            assert isinstance(p, Popen)
            out, err = p.communicate()
            if err:  # true (non-zero return code)
                print(f"commnad returned an error: {err.decode("utf-8")}")
            else:
                print(out.decode("utf-8").strip())

        while True:
            res = None
            cmd = input(f"{self.cwd}:> ")
            res = parse_cmd(cmd)

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
    t = Term(os.getcwd())
    t.run()

