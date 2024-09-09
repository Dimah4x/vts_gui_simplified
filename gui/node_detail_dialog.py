import tkinter as tk
from tkinter import ttk, messagebox
from utils.logging_utils import logger


class NodeDetailDialog(tk.Toplevel):
    def __init__(self, parent, node, chirpstack_client):
        super().__init__(parent)
        self.node = node
        self.chirpstack_client = chirpstack_client
        self.title(f"Node Details: {node.name}")
        self.geometry("400x300")
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        ttk.Label(frame, text=f"Name: {self.node.name}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(frame, text=f"Dev EUI: {self.node.dev_eui}").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(frame, text=f"Type: {self.node.device_type}").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(frame, text=f"Status: {self.node.status}").grid(row=3, column=0, sticky=tk.W)
        ttk.Label(frame, text=f"SNR: {self.node.snr} dB").grid(row=4, column=0, sticky=tk.W)
        ttk.Label(frame, text=f"RSSI: {self.node.rssi} dBm").grid(row=5, column=0, sticky=tk.W)

        ttk.Button(frame, text="Status Request", command=self.send_status_request).grid(row=6, column=0, pady=5)
        ttk.Button(frame, text="Reset Request", command=self.send_reset_request).grid(row=7, column=0, pady=5)
        ttk.Button(frame, text="Data Collection", command=self.send_data_collection).grid(row=8, column=0, pady=5)

    def send_status_request(self):
        self.send_command(b'\x01', "Status request")

    def send_reset_request(self):
        self.send_command(b'\x02', "Reset request")

    def send_data_collection(self):
        self.send_command(b'\x03', "Data collection request")

    def send_command(self, command, command_name):
        logger.log(f"Sending {command_name} to device {self.node.dev_eui}")
        try:
            success, message = self.chirpstack_client.enqueue_downlink(self.node.dev_eui, command)
            if success:
                messagebox.showinfo("Command Sent", f"{command_name} sent successfully.")
                logger.log(f"{command_name} sent successfully to device {self.node.dev_eui}")
            else:
                messagebox.showerror("Error", f"Failed to send {command_name}: {message}")
                logger.log(f"Failed to send {command_name} to device {self.node.dev_eui}: {message}")
        except Exception as e:
            error_message = f"Unexpected error sending {command_name}: {str(e)}"
            messagebox.showerror("Error", error_message)
            logger.log(error_message)