import curses


def main(screen):
    cmds = []
    idx = 0
    string = ""

    # Initialize screen properties
    curses.cbreak()
    curses.noecho()
    screen.keypad(True)  # Enable special keys like KEY_BACKSPACE

    while True:
        screen.clear()  # Clear screen before updating text
        screen.addstr(0, 0, string)  # Display the typed string at (0,0)
        screen.refresh()  # Update screen display

        char_code = screen.getch()

        # Handle backspace key
        if char_code in (curses.KEY_BACKSPACE, 127, 8):  # Covers various backspace codes
            if string:  # Only remove if string is not empty
                string = string[:-1]
        elif char_code in (curses.KEY_ENTER, 10):
            cmds.append(string)
            string = ""
            idx = 0
        elif char_code == curses.KEY_UP:
            if cmds:
                if idx < len(cmds):
                    idx += 1
                    string = cmds[-idx]
        elif char_code == curses.KEY_DOWN:
            if cmds:
                if idx > 1:
                    idx -= 1
                    string = cmds[-idx]
                else:
                    idx = 0
                    string = ""

        elif char_code == 27:  # ESC key (exit)
            break
        elif char_code == ord('q'):  # Quit when 'q' is pressed
            break
        elif 32 <= char_code <= 126:  # Only accept printable ASCII characters
            string += chr(char_code)

    return string  # Return the final string after exiting curses

# Run curses and get the final string
final_string = curses.wrapper(main)

# Now print the final string after curses has restored the terminal
print("\nFinal string:", final_string)
