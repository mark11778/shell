import os
import sys
import subprocess
from curses.ascii import isdigit


class term:
    SPECIAL_CHARS = set(['=', '/', '$'])

    def __init__(self, cwd):
        self.cwd = cwd
        self.built_in = None

    def cd(self, args):
        if len(args) == 1:
            print("Error cd takes two arguments")
            return
        if args[1] == "..":
            self.cwd = os.path.dirname(os.getcwd())
        else:
            if args[1] in os.listdir(self.cwd):
                self.cwd = os.path.join(self.cwd, args[1])

    def leave(self, args):
        if len(args) == 1:
            sys.exit(0)
        else:
            if args[1].isdigit():
                sys.exit(int(args[1]))
            else:
                print("Error leave takes one argument")

    def getcwd(self, args):
        if len(args) != 1:
            print("cwd takes only one argument")
        else:
            print(self.cwd)

    def export(self, args):
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

        while True:
            cmd = input(f"{self.cwd}:> ")
            arg = parse_input(cmd)
            if arg[0] in self.built_in:
                self.built_in[arg[0]](arg)
            else:
                p = subprocess.Popen(arg, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                if err: # true (non-zero return code)
                    print(f"commnad returned an error: {err.decode("utf-8")}")
                else:
                    print(out.decode("utf-8"))

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

