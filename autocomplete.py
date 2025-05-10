import os
from terminal import Term
from collections import deque

class autoComplete(Term):
    def __init__(self):
        # super().__init__(os.getcwd())
        self.cwd = os.getcwd()
        self.possible = None

    def relative_path(self, dirs):
        stack = []
        for dir in dirs:
            if dir == "..": # handling parent dirs
                if stack:
                    stack.pop()
                else:
                    stack.append(dir) # will have to go to parent dir
            elif dir and dir != ".":
                stack.append(dir)
        return stack

    def get_suggestion(self, cmd):
        dirs = cmd.split("/")
        prefix = dirs.pop()
        dirs = self.relative_path(dirs)

        new_path = self.cwd
        for dir in dirs:
            if dir == '..':
                new_path = os.path.dirname(new_path)
            else:
                new_path = os.path.join(new_path, dir)

        files = os.listdir(new_path)

        matches = deque()
        for file in files:
            if prefix:
                if not file.startswith(prefix):
                    continue
            matches.append(file)

        return matches

    def tab_pressed(self, cmd, changed=1):
        if changed == 1:
            self.possible = self.get_suggestion(cmd)

        if not self.possible:
            return ""
        return self.possible.popleft() if len(self.possible) > 1 else self.possible[0]

