import sys
import termios
import tty
from autocomplete import autoComplete

class TermIO:
    def __init__(self, base):
        self.base = base
        self.cmds = []
        self.idx = 0
        self.string = ""
        self.screen = None
        self.auto = autoComplete()

    def clear(self):
        sys.stdout.write('\r')
        sys.stdout.write('\x1b[2K')
        sys.stdout.write(f"{self.base}")

    def read_input(self):
        self.string = ""
        fb = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fb)
        changed = 1
        prefix = None

        try:
            tty.setraw(fb)
            sys.stdout.write(f"{self.base}")
            while True:
                ch = sys.stdin.read(1)
                if ch == '\t':
                    if prefix is None:
                        prefix = self.string.split(" ")[-1]
                    sug = self.auto.tab_pressed(prefix, changed)
                    changed = 0
                    idx,space = self.string.rfind("/"), self.string.rfind(" ")
                    if idx == -1:
                        self.string = self.string[:space + 1 ] + sug
                    else:
                        self.string = self.string[:idx + 1] + sug
                    self.clear()
                    sys.stdout.write(self.string)
                    sys.stdout.flush()
                    continue

                changed = 1
                prefix = None


                if ch == '\x1b':
                    nxt = sys.stdin.read(1)
                    if nxt == '[':
                        nxt = sys.stdin.read(1)
                        if nxt == 'A': # up arrow
                            if self.cmds and self.idx < len(self.cmds):
                                self.idx += 1
                                self.string = self.cmds[-self.idx]
                        if nxt == 'B': # down arrow
                            if self.idx > 1:
                                self.idx -= 1
                                self.string = self.cmds[-self.idx]
                            else:
                                self.string = ""
                                self.idx = 0
                        self.clear()
                        sys.stdout.write(self.string)
                        sys.stdout.flush()

                elif ch == '\r' or ch == '\n':
                    self.index = 1
                    self.cmds.append(self.string)
                    break
                elif ch == '\x7f':
                    if self.string:
                        self.string = self.string[:-1]
                        sys.stdout.write('\b \b')
                else:
                    self.string += ch
                    sys.stdout.write(ch)
                sys.stdout.flush()
        finally:
            termios.tcsetattr(fb, termios.TCSADRAIN, old_settings)
            print()

        return self.string

if __name__ == "__main__":
    t = TermIO()

