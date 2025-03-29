import tkinter as tk
from TermIO import TermIO

class twin:
    def __init__(self):
        self.mainWindow = None
        self.setup()

    def setup(self):
        """ initialize all the tkinter objects"""
        self.mainWindow = tk.Tk()
        self.mainWindow.title("Shell")
        self.mainWindow.geometry("600x600")
        self.mainWindow.resizable(False, False)

        self.text_widget = tk.Text(self.mainWindow, wrap=tk.WORD, font=("Helvetica", 12))
        self.text_widget.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=0)

        self.mainWindow.mainloop()

    def write(self, msg):
        """used to write output to terminal window"""
        self.text_widget.insert(tk.END, msg)
        self.text_widget.see(tk.END)

if __name__ == '__main__':
    io = TermIO("1345:")
    t = twin()

