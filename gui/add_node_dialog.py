import tkinter as tk
from tkinter import ttk, messagebox
from utils.logging_utils import logger

class AddNodeDialog(tk.Toplevel):
    def __init__(self, parent, chirpstack_client, node_manager):
        super().__init__(parent)
        self.chirpstack_client = chirpstack_client
        self.node_manager = node_manager
        self.title("Add New Node")
        self.node_added = False
        self.added_node = None
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        ttk.Label(frame, text="Device EUI:").grid(column=0, row=0, sticky=tk.W)
        self.dev_eui = ttk.Entry(frame, width=40)
        self.dev_eui.grid(column=1, row=0, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Name:").grid(column=0, row=1, sticky=tk.W)
        self.name = ttk.Entry(frame, width=40)
        self.name.grid(column=1, row=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Device Type:").grid(column=0, row=2, sticky=tk.W)
        self.device_type = ttk.Combobox(frame, values=["LiDAR unit", "Sound Unit", "Wearable Alert Unit"])
        self.device_type.grid(column=1, row=2, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Device Profile:").grid(column=0, row=3, sticky=tk.W)
        self.device_profiles = self.chirpstack_client.get_device_profiles()
        self.device_profile = ttk.Combobox(frame, values=[profile['name'] for profile in self.device_profiles])
        self.device_profile.grid(column=1, row=3, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Network Key (NwkKey):").grid(column=0, row=4, sticky=tk.W)
        self.nwk_key = ttk.Entry(frame, width=40)
        self.nwk_key.grid(column=1, row=4, sticky=(tk.W, tk.E))

        ttk.Button(frame, text="Add Node", command=self.add_node).grid(column=1, row=5, sticky=tk.E)

        for child in frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def add_node(self):
        dev_eui = self.dev_eui.get()
        name = self.name.get()
        device_type = self.device_type.get()
        device_profile_name = self.device_profile.get()
        nwk_key = self.nwk_key.get()

        if not dev_eui or not name or not device_type or not device_profile_name or not nwk_key:
            messagebox.showerror("Error", "All fields are required.")
            return

        device_profile_id = next((profile['id'] for profile in self.device_profiles if profile['name'] == device_profile_name), None)
        if not device_profile_id:
            messagebox.showerror("Error", "Invalid device profile selected.")
            return

        try:
            success, message = self.chirpstack_client.add_device(
                dev_eui, name, device_profile_id,
                self.chirpstack_client.app_id, nwk_key, device_type
            )
            if success:
                self.added_node = self.node_manager.add_node(dev_eui, name, device_type)
                self.node_added = True
                messagebox.showinfo("Success", f"Node {name} added successfully.")
                logger.log(f"Node {name} ({dev_eui}) added successfully")
                self.destroy()
            else:
                messagebox.showerror("Error", f"Failed to add node: {message}")
                logger.log(f"Failed to add node {name} ({dev_eui}): {message}")
        except Exception as e:
            error_message = f"Unexpected error adding node: {str(e)}"
            messagebox.showerror("Error", error_message)
            logger.log(error_message)

        logger.log(f"AddNodeDialog closing. node_added: {self.node_added}")
