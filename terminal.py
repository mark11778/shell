import os
import subprocess

class term:
    def __init__(self, cwd):
        self.cwd = cwd

    def strt(self):
        def parse_input(cmd):
            # remove white space
            cmd = cmd.strip()
            return cmd.split(" ")

        def cd(args):
            if len(args) == 1:
                print("Error cd takes two arguments")
                return
            if args[1] == "..":
                self.cwd = os.path.dirname(os.getcwd())
            else:
                if args[1] in os.listdir(self.cwd):
                    self.cwd = os.path.join(self.cwd, args[1])

        while True:
            cmd = input(f"{self.cwd}:> ")
            arg = parse_input(cmd)
            if "cd" in arg[1]:
                cd(arg)
            if "exit" in arg[1]:
                break
            else:
                p = subprocess.Popen(arg, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                if err != 0:
                    print(out.decode("utf-8"))
                else:
                    print(f"commnad returned an error: {err.decode("utf-8")}")