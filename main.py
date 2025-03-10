import os
from terminal import term
from tkwindow import twin



def main():
    print("Starting up terminal")
    t = term(os.getcwd())
    win = twin(t)


if __name__ == "__main__":
    main()
