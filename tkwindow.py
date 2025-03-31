import os, sys, subprocess, io
import tkinter as tk
from autocomplete import autoComplete
from terminal import Term

class TerminalApp:
    def __init__(self):
        # Initialize main window and text widget
        self.root = tk.Tk()
        self.root.title("Terminal")
        self.text = tk.Text(self.root, wrap=tk.WORD, font=("Courier New", 12))
        self.text.pack(expand=True, fill=tk.BOTH)

        # Initialize state variables
        self.cmd = ""                         # Current input after the prompt
        self.history = []                     # Command history list
        self.history_index = 0                # Index for navigating history (0 = no selection)
        self.auto = autoComplete()            # Autocomplete helper
        self.term = Term(os.getcwd())         # Terminal logic (for built-in commands, etc.)
        self.term.built_in = {                # Set up built-in commands
            "cd": self.term.cd,
            "exit": self.term.leave,
            "cwd": self.term.getcwd,
            "export": self.term.export
        }
        self.tab_prefix = None                # Current prefix for Tab suggestions (None if not in a cycle)
        self.exiting = False                  # Flag to indicate if an exit command was issued

        # Insert the initial prompt
        self.insert_prompt()

        # Bind key events for handling input
        self.text.bind("<Return>", self.on_enter)
        self.text.bind("<BackSpace>", self.on_backspace)
        self.text.bind("<Left>", self.on_left)
        self.text.bind("<Up>", self.on_up)
        self.text.bind("<Down>", self.on_down)
        self.text.bind("<Tab>", self.on_tab)
        self.text.bind("<KeyPress>", self.on_keypress)

    def insert_prompt(self):
        """Display a prompt and reset input state for a new line."""
        prompt_str = f"{self.term.cwd}:> "              # e.g., current directory prompt
        # Ensure the prompt is on a new line
        if self.text.index("end-1c") != "1.0":          # if not at the very start
            if self.text.get("end-2c") != "\n":         # if last char isn't already a newline
                self.text.insert(tk.END, "\n")
        self.text.insert(tk.END, prompt_str)
        # Mark the end of prompt (start of user input)
        self.prompt_index = self.text.index("insert")
        # Reset input buffer and Tab state
        self.cmd = ""
        self.tab_prefix = None

    def on_keypress(self, event):
        """Handle regular character keys: insert into text and update self.cmd."""
        # Ignore control characters (handled in specific event bindings)
        if not event.char or event.char in ("\r", "\n", "\t", "\x08", "\x7f"):
            return  # Do nothing for Enter, Tab, Backspace, etc. here
        # Determine insertion position relative to prompt
        cur_pos = self.text.index("insert")
        p_line, p_col = self.prompt_index.split('.')
        c_line, c_col = cur_pos.split('.')
        if p_line == c_line:
            # Cursor is on the prompt’s line – calculate offset from prompt
            offset = int(c_col) - int(p_col)
        else:
            # (In practice, input stays on one line; this is a safeguard)
            offset = len(self.cmd)
        # Update internal buffer with the new character
        self.cmd = self.cmd[:offset] + event.char + self.cmd[offset:]
        # Insert the character into the Text widget at the cursor
        self.text.insert(cur_pos, event.char)
        # Since content changed, reset Tab completion cycle
        self.tab_prefix = None
        return "break"  # Prevent default text insertion

    def on_backspace(self, event):
        """Handle Backspace: delete character to left of cursor if within input."""
        cur_pos = self.text.index("insert")
        # If cursor is at prompt boundary, disallow backspace (nothing to delete)
        if cur_pos == self.prompt_index:
            return "break"
        if len(self.cmd) == 0:
            return "break"  # No input to delete (safety check)
        # Compute index of character to delete (one position left of cursor)
        del_index = self.text.index("insert - 1c")
        # Guard: if deletion would go into the prompt area, block it
        p_line, p_col = self.prompt_index.split('.')
        d_line, d_col = del_index.split('.')
        if p_line == d_line and int(d_col) < int(p_col):
            return "break"
        # Remove the character from both the widget and the buffer
        self.text.delete(del_index)
        if p_line == d_line:
            offset = int(d_col) - int(p_col)    # position in self.cmd
        else:
            offset = int(d_col)
        self.cmd = self.cmd[:offset] + self.cmd[offset+1:]
        # Reset Tab completion state on deletion
        self.tab_prefix = None
        return "break"

    def on_left(self, event):
        """Prevent moving cursor into the prompt area with Left arrow."""
        if self.text.index("insert") == self.prompt_index:
            # Cursor is at the start of input; block left movement
            return "break"
        # If cursor is within input text, allow the move but clear Tab state
        self.tab_prefix = None
        # (Do not return "break" here, so the default cursor move occurs)

    def on_up(self, event):
        """Recall previous command from history on Up arrow."""
        if self.history and self.history_index < len(self.history):
            self.history_index += 1
            # Get the command that is `history_index` from the end (1 = last)
            recalled_cmd = self.history[-self.history_index]
            self.replace_input_with(recalled_cmd)
        return "break"  # Override default Up-arrow text behavior

    def on_down(self, event):
        """Recall next (more recent) command or clear input on Down arrow."""
        if self.history_index > 1:
            # Move one step forward in history
            self.history_index -= 1
            next_cmd = self.history[-self.history_index]
            self.replace_input_with(next_cmd)
        elif self.history_index == 1:
            # If at most recent history entry, down arrow clears the input
            self.history_index = 0
            self.replace_input_with("")
        return "break"

    def on_tab(self, event):
        """Autocomplete the current input token (file/path completion)."""
        # If starting a new autocomplete session, determine the prefix
        if self.tab_prefix is None:
            if self.cmd == "":
                return "break"  # Nothing to autocomplete on empty input
            # Set prefix to the last word or path segment typed
            self.tab_prefix = self.cmd.split(" ")[-1]
            changed = 1  # signal to recompute suggestions
        else:
            # Continuing an autocomplete cycle
            changed = 0
        suggestion = self.auto.tab_pressed(self.tab_prefix, changed)
        if not suggestion:
            return "break"  # No suggestion available, ignore Tab
        # Determine which part of self.cmd to replace with the suggestion
        last_slash = self.cmd.rfind("/")
        last_space = self.cmd.rfind(" ")
        if last_slash == -1:
            # Replace everything after the last space (if any)
            replace_start = (last_space + 1) if last_space != -1 else 0
        else:
            # Replace everything after the last slash in a path
            replace_start = last_slash + 1
        # Construct the new command with the completed token
        new_cmd = self.cmd[:replace_start] + suggestion
        # Replace the input line with the new completed command
        current_prefix = self.tab_prefix      # preserve current prefix
        self.replace_input_with(new_cmd)
        self.tab_prefix = current_prefix      # keep prefix to allow cycling on next Tab
        return "break"

    def replace_input_with(self, new_text):
        """Utility to replace the current input (after the prompt) with new_text."""
        # Delete existing input text in the widget
        start = self.prompt_index
        end = self.text.index("end-1c")
        self.text.delete(start, end)
        # Insert the new text and update the buffer
        self.text.insert(start, new_text)
        self.cmd = new_text
        # Move cursor to end of the input
        self.text.mark_set("insert", "end-1c")
        # By default, reset tab prefix (except when explicitly preserved during Tab cycling)
        self.tab_prefix = None

    def on_enter(self, event):
        """Handle Enter: execute the command and prepare for a new prompt."""
        # Get the full command from the buffer and trim it
        command = self.cmd.strip()
        # Print a newline to the widget to emulate the Enter key press
        self.text.insert(tk.END, "\n")
        # Add the command to history if not empty
        if command:
            self.history.append(command)
        self.history_index = 0  # reset history navigation index
        # Execute the command through handle_command
        self.handle_command(command)
        # If an exit command was executed, stop (application will close)
        if self.exiting:
            return "break"
        # Otherwise, insert a new prompt for the next input
        self.insert_prompt()
        return "break"

    def handle_command(self, cmd):
        """Execute the given command string (built-in or external)."""
        if cmd == "":
            return  # Nothing to do for empty command (just a blank line)
        args = cmd.split()
        name = args[0]
        if name in self.term.built_in:
            # Handle built-in commands internally
            if name in ("exit", "leave"):
                # For exit, terminate the application
                self.exiting = True
                self.root.destroy()
                return
            # Redirect stdout to capture built-in command output
            stdout_backup = sys.stdout
            output_buffer = io.StringIO()
            sys.stdout = output_buffer
            try:
                self.term.built_in[name](args)      # execute built-in command
            finally:
                sys.stdout = stdout_backup
            output = output_buffer.getvalue()
            if output:  # Write any captured output to the terminal widget
                self.text.insert(tk.END, output.strip() + "\n")
            if name == "cd":
                # Update working directory for prompt and autocomplete
                self.auto.cwd = self.term.cwd
        else:
            # Execute external system command
            try:
                proc = subprocess.Popen(args, cwd=self.term.cwd,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = proc.communicate()
            except Exception as e:
                # If command execution failed (e.g., command not found)
                out, err = b"", str(e).encode()
            # Display command output and errors (if any) in the widget
            if out:
                self.text.insert(tk.END, out.decode().strip() + "\n")
            if err:
                self.text.insert(tk.END, err.decode().strip() + "\n")
