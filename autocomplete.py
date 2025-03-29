import os
from collections import deque

class autoComplete():
    def __init__(self, cwd):
        self.cwd = cwd
        self.possible = None

    def update_cwd(self, new_cwd):
        self.cwd = new_cwd

    def relative_path(self, dirs):
        #TODO: figure out how to do the back dirs
        new_dirs = []
        if len(dirs) >= 2:
            l, r = 0, 1
            new_dirs.append(dirs[l])
            prefix = dirs[-1]
            for _ in range(1, len(dirs) - 1):
                if dirs[r].strip() == "..":
                    new_dirs.pop()
                else:
                    new_dirs.append(dirs[r])
                l = r
                r += 1
        else:
            return dirs
        return new_dirs

    def get_sugegestion(self, cmd):
        dirs = cmd.split("/")
        prefix = dirs.pop()
        dirs = self.relative_path(dirs)

        new_path = self.cwd
        for dir in dirs:
            new_path = os.path.join(new_path, dir)

        files = os.listdir(new_path)

        matches = deque()
        for file in files:
            if file.startswith(prefix):
                matches.append(file)

        return matches

    def tab_pressed(self, cmd, changed=1):
        if changed == 1:
            self.possible = self.get_sugegestion(cmd)
        return self.possible.popleft() if len(self.possible) > 1 else self.possible[0]










