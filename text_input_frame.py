import tkinter
from tkinter import ttk
from gpt import ChatSession
import threading

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
        self.chat_button = ttk.Button(self, text="Send", command=self.send_message)
        self.chat_button.grid(row=2, column=1, sticky="w")

        self.chat_session = ChatSession()
        self.input_entry.bind("<Return>", self.send_message)

    def send_message(self, event=None):
        user_input = self.input_text.get()
        if not user_input:
            return

        self.input_text.set("")
        self.textbox.insert(tkinter.END, "You: " + user_input + "\n")
        
        self.textbox.see(tkinter.END)

        def send_message_thread():
            answer = self.chat_session.chat(user_input)
            self.textbox.insert(tkinter.END, "AI: " + answer + "\n")

        threading.Thread(target=send_message_thread).start()