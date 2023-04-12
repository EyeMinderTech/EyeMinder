import tkinter
from tkinter import ttk
import global_dict

class CheckBox(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="设置", padding=15)

        self.show_result = tkinter.BooleanVar(self, False)
        self.show_keypoint = tkinter.BooleanVar(self, True)

        self.add_widgets()

    def add_widgets(self):
        self.checkbox_1 = ttk.Checkbutton(self, text="设置")
        self.checkbox_1.grid(row=0, column=0, pady=(0, 10), sticky="w")

        self.checkbox_2 = ttk.Checkbutton(self, text="检测结果", variable=self.show_result, command=self.on_checkbox_changed)
        self.checkbox_2.grid(row=1, column=0, padx=(30, 0), pady=(5, 10), sticky="w")
        self.checkbox_3 = ttk.Checkbutton(self, text="关键点坐标", variable=self.show_keypoint, command=self.on_checkbox_changed)
        self.checkbox_3.grid(row=2, column=0, padx=(30, 0), pady=10, sticky="w")

        self.checkbox_4 = ttk.Checkbutton(self, text="todo")
        self.checkbox_4.state({"disabled", "!alternate"})
        self.checkbox_4.grid(row=3, column=0, padx=(30, 0), pady=(10, 0), sticky="w")

    def on_checkbox_changed(self):
        camera_detection = global_dict.get_value("camera_detection")
        camera_detection.show_keypoint = self.show_keypoint.get()
        camera_detection.show_result = self.show_result.get()
        print("on changed")
