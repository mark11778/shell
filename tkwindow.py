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
        self.cmd = ""
        self.history = []
        self.history_index = 0
        self.auto = autoComplete()
        self.term = Term(os.getcwd())
        self.term.built_in = {
            "cd": self.term.cd,
            "exit": self.term.leave,
            "cwd": self.term.getcwd,
            "export": self.term.export,
            "clear" : None
        }
        self.tab_prefix = None
        self.exiting = False

        # Insert the initial prompt
        self.insert_prompt()

        self.text.bind("<Return>", self.on_enter)
        self.text.bind("<BackSpace>", self.on_backspace)
        self.text.bind("<Left>", self.on_left)
        self.text.bind("<Up>", self.on_up)
        self.text.bind("<Down>", self.on_down)
        self.text.bind("<Tab>", self.on_tab)
        self.text.bind("<KeyPress>", self.on_keypress)

    def insert_prompt(self):
        """Display a prompt and reset input state for a new line."""
        prompt_str = f"{self.term.cwd}:> "
        if self.text.index("end-1c") != "1.0":
            if self.text.get("end-2c") != "\n":
                self.text.insert(tk.END, "\n")
        self.text.insert(tk.END, prompt_str)
        self.prompt_index = self.text.index("insert")
        self.cmd = ""
        self.tab_prefix = None

    def on_keypress(self, event):
        """Handle regular character keys: insert into text and update self.cmd."""
        if not event.char or event.char in ("\r", "\n", "\t", "\x08", "\x7f"):
            return  # these are handled else where
        cur_pos = self.text.index("insert")
        p_line, p_col = self.prompt_index.split('.')
        c_line, c_col = cur_pos.split('.')
        if p_line == c_line:
            offset = int(c_col) - int(p_col)
        else:
            offset = len(self.cmd)
        self.cmd = self.cmd[:offset] + event.char + self.cmd[offset:]
        self.text.insert(cur_pos, event.char)
        self.tab_prefix = None
        return "break"

    def on_backspace(self, event):
        """Handle Backspace: delete character to left of cursor if within input."""
        cur_pos = self.text.index("insert")
        if cur_pos == self.prompt_index:
            return "break"
        if len(self.cmd) == 0:
            return "break"

        del_index = self.text.index("insert - 1c")
        p_line, p_col = self.prompt_index.split('.')
        d_line, d_col = del_index.split('.')
        if p_line == d_line and int(d_col) < int(p_col):
            return "break"
        self.text.delete(del_index)
        if p_line == d_line:
            offset = int(d_col) - int(p_col)    # position in self.cmd
        else:
            offset = int(d_col)
        self.cmd = self.cmd[:offset] + self.cmd[offset+1:]
        self.tab_prefix = None
        return "break"

    def on_left(self, event):
        """Prevent moving cursor into the prompt area with Left arrow."""
        if self.text.index("insert") == self.prompt_index:
            return "break"
        self.tab_prefix = None

    def on_up(self, event):
        """Recall previous command from history on Up arrow."""
        if self.history and self.history_index < len(self.history):
            self.history_index += 1
            recalled_cmd = self.history[-self.history_index]
            self.replace_input_with(recalled_cmd)
        return "break"

    def on_down(self, event):
        """Recall next (more recent) command or clear input on Down arrow."""
        if self.history_index > 1:
            self.history_index -= 1
            next_cmd = self.history[-self.history_index]
            self.replace_input_with(next_cmd)
        elif self.history_index == 1:
            self.history_index = 0
            self.replace_input_with("")
        return "break"

    def on_tab(self, event):
        """Autocomplete the current input token (file/path completion)."""
        if self.tab_prefix is None:
            if self.cmd == "":
                return "break"
            self.tab_prefix = self.cmd.split(" ")[-1]
            changed = 1
        else:
            changed = 0
        suggestion = self.auto.tab_pressed(self.tab_prefix, changed)
        if not suggestion:
            return "break"
        last_slash = self.cmd.rfind("/")
        last_space = self.cmd.rfind(" ")
        if last_slash == -1:
            replace_start = (last_space + 1) if last_space != -1 else 0
        else:
            replace_start = last_slash + 1
        new_cmd = self.cmd[:replace_start] + suggestion
        current_prefix = self.tab_prefix
        self.replace_input_with(new_cmd)
        self.tab_prefix = current_prefix
        return "break"

    def replace_input_with(self, new_text):
        """Utility to replace the current input (after the prompt) with new_text."""
        start = self.prompt_index
        end = self.text.index("end-1c")
        self.text.delete(start, end)
        self.text.insert(start, new_text)
        self.cmd = new_text
        self.text.mark_set("insert", "end-1c")
        self.tab_prefix = None

    def on_enter(self, event):
        """Handle Enter: execute the command and prepare for a new prompt."""
        command = self.cmd.strip()
        self.text.insert(tk.END, "\n")
        if command:
            self.history.append(command)
        self.history_index = 0
        self.handle_command(command)
        if self.exiting:
            return "break"
        self.insert_prompt()
        return "break"

    def handle_command(self, cmd):
        """Execute the given command string (built-in or external)."""
        if cmd == "":
            return
        args = cmd.split()
        name = args[0]
        if name in self.term.built_in:
            if name in ("exit", "leave"):
                self.exiting = True
                self.root.destroy()
                return
            if name == "clear":
                self.text.delete("1.0", "end")
                return
            stdout_backup = sys.stdout
            output_buffer = io.StringIO()
            sys.stdout = output_buffer
            try:
                self.term.built_in[name](args)
            finally:
                sys.stdout = stdout_backup
            output = output_buffer.getvalue()
            if output:
                self.text.insert(tk.END, output.strip() + "\n")
            if name == "cd":
                self.auto.cwd = self.term.cwd
        else:
            try:
                proc = subprocess.Popen(args, cwd=self.term.cwd,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = proc.communicate()
            except Exception as e:
                out, err = b"", str(e).encode()
            if out:
                self.text.insert(tk.END, out.decode().strip() + "\n")
            if err:
                self.text.insert(tk.END, err.decode().strip() + "\n")
