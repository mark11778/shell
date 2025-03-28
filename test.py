import sys
import termios
import tty


def read_raw_line():
    input_str = ""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch == '\r' or ch == '\n':
                break
            elif ch == '\x7f':  # Backspace
                input_str = input_str[:-1]
                sys.stdout.write('\b \b')
                sys.stdout.flush()
            else:
                input_str += ch
                sys.stdout.write(ch)
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print()  # Move to next line

    return input_str


if __name__ == "__main__":
    print("Type something (raw input):")
    result = read_raw_line()
    print("You typed:", result)