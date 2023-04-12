import tkinter
from tkinter import ttk

class RadioButton(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="预训练模型", padding=15)

        self.var = tkinter.IntVar()

        self.add_widgets()

    def clickRadioButton(self):
        print("RadioButton Clicked")
        print(self.var.get())

    def add_widgets(self):
        self.radio_1 = ttk.Radiobutton(self, text="Model 1", variable=self.var, value=0, command=self.clickRadioButton)
        self.radio_1.grid(row=0, column=0, pady=(0, 10), sticky="w")

        self.radio_1 = ttk.Radiobutton(self, text="Model 2", variable=self.var, value=1, command=self.clickRadioButton)
        self.radio_1.grid(row=1, column=0, pady=10, sticky="w")

        self.radio_1 = ttk.Radiobutton(self, text="Model 3", state="disabled")
        self.radio_1.grid(row=2, column=0, pady=(10, 0), sticky="w")