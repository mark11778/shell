import os
from terminal import Term
from tkwindow import twin


class prog:
    def __init__(self):
        self.t = Term(os.getcwd())
        self.win = twin()

    def __print__(self, msg):
        self.win.write(msg)


def main():
    print("Starting up terminal")
    t = Term(os.getcwd())
    win = twin(t)


if __name__ == "__main__":
    main()
