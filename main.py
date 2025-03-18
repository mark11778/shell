import os
from terminal import Term
from tkwindow import twin



def main():
    print("Starting up terminal")
    t = Term(os.getcwd())
    win = twin(t)


if __name__ == "__main__":
    main()
