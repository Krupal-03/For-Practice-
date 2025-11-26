import tkinter as tk
class Root(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("300x300")
        self.title("Simple_Two_Doo")
        self.configure(bg='lightblue')
        self.label=tk.Label(self, text="hi hello ")
        self.label.pack()
if __name__ == "__main__":
    root=Root()
    root.mainloop()