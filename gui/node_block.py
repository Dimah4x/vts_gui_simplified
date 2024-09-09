import tkinter as tk
from tkinter import ttk
from utils.logging_utils import logger


class NodeBlock(ttk.Frame):
    def __init__(self, master, node, on_click):
        super().__init__(master, borderwidth=2, relief="raised", padding=5)
        self.node = node
        self.on_click = on_click
        self.setup_ui()
        self.blinking = False

    def setup_ui(self):
        self.name_label = ttk.Label(self, text=self.node.name, font=("TkDefaultFont", 12, "bold"))
        self.name_label.pack()

        self.type_label = ttk.Label(self, text=f"Type: {self.node.device_type}")
        self.type_label.pack()

        self.status_label = ttk.Label(self, text=f"Status: {self.node.status}")
        self.status_label.pack()

        self.bind("<Button-1>", self.handle_left_click)
        self.bind("<Button-3>", self.handle_right_click)

        for child in self.winfo_children():
            child.bind("<Button-1>", self.handle_left_click)
            child.bind("<Button-3>", self.handle_right_click)

        self.update_display()

    def update_display(self):
        logger.log(f"Updating display for node: {self.node.name}, Status: {self.node.status}")
        self.status_label.config(text=f"Status: {self.node.status}")

        if self.node.has_alert:
            logger.log(f"Node {self.node.name} has alert, setting Red style")
            self.configure(style="Red.TFrame")
            if not self.blinking:
                self.blinking = True
                self.blink()
        elif self.node.status == "Online":
            logger.log(f"Node {self.node.name} is online, setting Green style")
            self.configure(style="Green.TFrame")
            self.blinking = False
        else:
            logger.log(f"Node {self.node.name} is offline, setting Gray style")
            self.configure(style="Gray.TFrame")
            self.blinking = False

        self.master.update_idletasks()
        logger.log(f"Display updated for node: {self.node.name}")

    def blink(self):
        if self.node.has_alert and self.blinking:
            current_style = self.cget("style")
            new_style = "Red.TFrame" if current_style != "Red.TFrame" else "Gray.TFrame"
            self.configure(style=new_style)
            self.after(500, self.blink)
        else:
            self.update_display()

    def handle_left_click(self, event):
        self.event_generate('<<NodeClicked>>', when="tail")

    def handle_right_click(self, event):
        self.event_generate('<<NodeRightClicked>>', when="tail", x=event.x, y=event.y)