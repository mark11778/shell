import tkinter as tk

class twin:
    def __init__(self, term):
        self.term = term
        self.mainWindow = None
        self.setup()
        self.name_var = tk.StringVar()
        self.passw_var = tk.StringVar()

    def setup(self):
        self.mainWindow = tk.Tk()
        self.mainWindow.title("Shell")
        self.mainWindow.geometry("400x400")
        self.mainWindow.resizable(True, True)
        name_label = tk.Label(self.mainWindow, text='Username', font=('calibre', 10, 'bold'))

        # creating a entry for input
        # name using widget Entry
        name_entry = tk.Entry(self.mainWindow, textvariable=self.name_var, font=('calibre', 10, 'normal'))

        # creating a label for password
        passw_label = tk.Label(self.mainWindow, text='Password', font=('calibre', 10, 'bold'))

        # creating a entry for password
        passw_entry = tk.Entry(self.mainWindow, textvariable=self.passw_var, font=('calibre', 10, 'normal'), show='*')

        # creating a button using the widget 
        # Button that will call the submit function 
        sub_btn = tk.Button(self.mainWindow, text='Submit', command=self.submit)

        # placing the label and entry in
        # the required position using grid
        # method
        name_label.grid(row=0, column=0)
        name_entry.grid(row=0, column=1)
        passw_label.grid(row=1, column=0)
        passw_entry.grid(row=1, column=1)
        sub_btn.grid(row=2, column=1)
        
        self.mainWindow.mainloop()

    def submit(self):
        name = self.name_var.get()
        password = self.passw_var.get()

        print("The name is : " + name)
        print("The password is : " + password)

        self.name_var.set("")
        self.passw_var.set("")
