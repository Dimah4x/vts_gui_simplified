import tkinter as tk
from tkinter import ttk
from utils.logging_utils import logger

class LogWindow(tk.Toplevel):
    def __init__(self, parent, title, log_type="general"):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x400")
        self.log_type = log_type
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        self.text = tk.Text(frame, wrap=tk.WORD, width=80, height=20)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)

        self.load_log_content()

    def load_log_content(self):
        try:
            log_file = logger.alert_log_file if self.log_type == "alert" else logger.general_log_file
            with open(log_file, 'r') as file:
                content = file.read()
            self.text.insert(tk.END, content)
        except Exception as e:
            self.text.insert(tk.END, f"Error loading log file: {str(e)}")
        self.text.config(state=tk.DISABLED)