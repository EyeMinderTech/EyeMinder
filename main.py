import tkinter
from tkinter import ttk
import sv_ttk
from face_detection_frame import FaceDetectionFrame
from check_box import CheckBox
from radio_button import RadioButton
from text_input_frame import TextInputFrame
from camera_detection import FatigueDetection
import global_dict

global_dict._init()
global_dict.set_value('camera_detection', FatigueDetection())

class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)

        for index in range(2):
            self.columnconfigure(index, weight=1)
            self.rowconfigure(index, weight=1)

        CheckBox(self).grid(row=0, column=0, padx=(0, 10), pady=(0, 20), sticky="nsew")
        RadioButton(self).grid(row=1, column=0, padx=(0, 10), sticky="nsew")
        text_input_frame = TextInputFrame(self)
        text_input_frame.grid(row=1, column=1, rowspan=1, padx=(10, 0), pady=10, sticky="nsew")
        FaceDetectionFrame(self).grid(row=0, column=1, rowspan=1, padx=(10, 0), pady=10, sticky="nsew")
        global_dict.get_value('camera_detection').text_input_frame = text_input_frame

def main():
    root = tkinter.Tk()
    root.title("EyeMinder")

    sv_ttk.set_theme("light")

    App(root).pack(expand=True, fill="both")

    root.mainloop()

if __name__ == "__main__":
    main()