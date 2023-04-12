import tkinter
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import global_dict

class FaceDetectionFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.camera_detection = global_dict.get_value("camera_detection")
        frame_size = self.camera_detection.get_frame_size()
        self.canvas = tkinter.Canvas(self, width=frame_size[0], height=frame_size[1])
        self.canvas.pack(expand=True, fill="both")

        self.update_frame()

    def update_frame(self):
        frame = cv2.cvtColor(self.camera_detection.image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)
        self.canvas.create_image(0, 0, anchor="nw", image=photo)
        self.canvas.image = photo
        self.camera_detection.detect_fatigue()
        self.after(20, self.update_frame)