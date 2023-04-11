
import tkinter
from tkinter import ttk

import sv_ttk

import cv2
from PIL import Image, ImageTk
from camera_detection import *
from gpt import *
import threading

camera_detection = FatigueDetection()


class FaceDetectionFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        global camera_detection
        frame_size = camera_detection.get_frame_size()
        self.canvas = tkinter.Canvas(
            self, width=frame_size[0], height=frame_size[1])
        self.canvas.pack(expand=True, fill="both")

        # self.capture = cv2.VideoCapture(0)
        self.update_frame()

    def update_frame(self):
        # ret, frame = self.capture.read()
        # if ret:
        #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #     image = Image.fromarray(frame)
        #     photo = ImageTk.PhotoImage(image=image)
        #     self.canvas.create_image(0, 0, anchor="nw", image=photo)
        #     self.canvas.image = photo
        # self.after(10, self.update_frame)
        frame = cv2.cvtColor(camera_detection.image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)
        self.canvas.create_image(0, 0, anchor="nw", image=photo)
        self.canvas.image = photo
        camera_detection.detect_fatigue()
        self.after(20, self.update_frame)


class CheckBox(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="设置", padding=15)

        self.show_result = tkinter.BooleanVar(self, False)
        self.show_keypoint = tkinter.BooleanVar(self, True)

        self.add_widgets()

    def add_widgets(self):
        self.checkbox_1 = ttk.Checkbutton(self, text="设置")
        self.checkbox_1.grid(row=0, column=0, pady=(0, 10), sticky="w")

        self.checkbox_2 = ttk.Checkbutton(
            self, text="检测结果", variable=self.show_result, command=self.on_checkbox_changed)
        self.checkbox_2.grid(row=1, column=0, padx=(
            30, 0), pady=(5, 10), sticky="w")

        self.checkbox_3 = ttk.Checkbutton(
            self, text="关键点坐标", variable=self.show_keypoint, command=self.on_checkbox_changed)
        self.checkbox_3.grid(row=2, column=0, padx=(
            30, 0), pady=10, sticky="w")

        # self.switch = ttk.Checkbutton(
        #     self.tab_1, text="Dark theme", style="Switch.TCheckbutton", command=sv_ttk.toggle_theme
        # )
        # self.switch.grid(row=1, column=0, columnspan=2, pady=10)

        self.checkbox_4 = ttk.Checkbutton(self, text="todo")
        self.checkbox_4.state({"disabled", "!alternate"})
        self.checkbox_4.grid(row=3, column=0, padx=(
            30, 0), pady=(10, 0), sticky="w")

    def on_checkbox_changed(self):
        global camera_detection
        camera_detection.show_keypoint = self.show_keypoint.get()
        camera_detection.show_result = self.show_result.get()
        print("on changed")


class RadioButton(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="预训练模型", padding=15)

        self.var = tkinter.IntVar()

        self.add_widgets()

    def clickRadioButton(self):
        print("RadioButton Clicked")
        print(self.var.get())

    def add_widgets(self):
        self.radio_1 = ttk.Radiobutton(
            self, text="Model 1", variable=self.var, value=0, command=self.clickRadioButton)
        self.radio_1.grid(row=0, column=0, pady=(0, 10), sticky="w")

        self.radio_1 = ttk.Radiobutton(
            self, text="Model 2", variable=self.var, value=1, command=self.clickRadioButton)
        self.radio_1.grid(row=1, column=0, pady=10, sticky="w")

        self.radio_1 = ttk.Radiobutton(self, text="Model 3", state="disabled")
        self.radio_1.grid(row=2, column=0, pady=(10, 0), sticky="w")


class TextInputFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.textbox = tkinter.Text(self)
        self.textbox.grid(row=0, column=0, sticky="nsew")

        self.input_label = ttk.Label(self, text="Input:")
        self.input_label.grid(row=1, column=0, sticky="w")

        self.input_text = tkinter.StringVar(value="")
        self.input_entry = ttk.Entry(self, textvariable=self.input_text)
        self.input_entry.grid(row=2, column=0, sticky="ew")
        self.chat_button = ttk.Button(
            self, text="Send", command=self.send_message)
        self.chat_button.grid(row=2, column=1, sticky="w")

        self.chat_session = ChatSession()
        self.input_entry.bind("<Return>", self.send_message)

    def send_message(self):
        # Retrieve user input
        user_input = self.input_text.get()
        # 如果输入框中没有内容，直接返回
        if not user_input:
            return

        self.input_text.set("")  # Clear the input_entry widget
        self.textbox.insert(tkinter.END, "You: " + user_input + "\n")

        self.textbox.see(tkinter.END)  # Scroll to the bottom of the textbox

        def send_message_thread():
            # 将发送到GPT API的操作放在线程中运行
            answer = self.chat_session.chat(user_input)
            # Display answer in textbox
            self.textbox.insert(tkinter.END, "AI: " + answer + "\n")

        threading.Thread(target=send_message_thread).start()  # 启动线程


class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)

        for index in range(2):
            self.columnconfigure(index, weight=1)
            self.rowconfigure(index, weight=1)

        CheckBox(self).grid(row=0, column=0, padx=(
            0, 10), pady=(0, 20), sticky="nsew")
        RadioButton(self).grid(row=1, column=0, padx=(0, 10), sticky="nsew")
        text_input_frame = TextInputFrame(self)
        text_input_frame.grid(row=1, column=1, rowspan=1,
                              padx=(10, 0), pady=10, sticky="nsew")
        FaceDetectionFrame(self).grid(
            row=0, column=1, rowspan=1, padx=(10, 0), pady=10, sticky="nsew")
        global camera_detection
        camera_detection.text_input_frame = text_input_frame


def main():
    root = tkinter.Tk()
    root.title("EyeMinder")

    sv_ttk.set_theme("light")

    App(root).pack(expand=True, fill="both")

    root.mainloop()


if __name__ == "__main__":
    main()
