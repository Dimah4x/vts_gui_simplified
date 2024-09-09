import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import save_config
from networking.chirpstack_client import ChirpStackClient


class ConfigDialog(tk.Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.title("ChirpStack and MQTT Configuration")
        self.config = config
        self.config_complete = False
        self.devices = []
        self.setup_ui()

    def setup_ui(self):
        frame = ttk.Frame(self, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # ChirpStack configuration
        ttk.Label(frame, text="ChirpStack Configuration", font=("TkDefaultFont", 12, "bold")).grid(column=0, row=0,
                                                                                                   columnspan=2,
                                                                                                   sticky=tk.W)

        ttk.Label(frame, text="Server Address:").grid(column=0, row=1, sticky=tk.W)
        self.server_address = ttk.Entry(frame, width=40)
        self.server_address.grid(column=1, row=1, sticky=(tk.W, tk.E))
        self.server_address.insert(0, self.config.get('server_address', ''))

        ttk.Label(frame, text="Server Port:").grid(column=0, row=2, sticky=tk.W)
        self.server_port = ttk.Entry(frame, width=10)
        self.server_port.grid(column=1, row=2, sticky=(tk.W, tk.E))
        self.server_port.insert(0, self.config.get('server_port', ''))

        ttk.Label(frame, text="API Token:").grid(column=0, row=3, sticky=tk.W)
        self.api_token = ttk.Entry(frame, width=40, show="*")
        self.api_token.grid(column=1, row=3, sticky=(tk.W, tk.E))
        self.api_token.insert(0, self.config.get('api_token', ''))

        ttk.Label(frame, text="Application ID:").grid(column=0, row=4, sticky=tk.W)
        self.app_id = ttk.Entry(frame, width=10)
        self.app_id.grid(column=1, row=4, sticky=(tk.W, tk.E))
        self.app_id.insert(0, self.config.get('app_id', ''))

        ttk.Label(frame, text="Tenant ID:").grid(column=0, row=5, sticky=tk.W)
        self.tenant_id = ttk.Entry(frame, width=10)
        self.tenant_id.grid(column=1, row=5, sticky=(tk.W, tk.E))
        self.tenant_id.insert(0, self.config.get('tenant_id', ''))

        # MQTT configuration
        ttk.Label(frame, text="MQTT Configuration", font=("TkDefaultFont", 12, "bold")).grid(column=0, row=6,
                                                                                             columnspan=2, sticky=tk.W,
                                                                                             pady=(10, 0))

        ttk.Label(frame, text="MQTT Broker:").grid(column=0, row=7, sticky=tk.W)
        self.mqtt_broker = ttk.Entry(frame, width=40)
        self.mqtt_broker.grid(column=1, row=7, sticky=(tk.W, tk.E))
        self.mqtt_broker.insert(0, self.config.get('mqtt_broker', ''))

        ttk.Label(frame, text="MQTT Port:").grid(column=0, row=8, sticky=tk.W)
        self.mqtt_port = ttk.Entry(frame, width=10)
        self.mqtt_port.grid(column=1, row=8, sticky=(tk.W, tk.E))
        self.mqtt_port.insert(0, self.config.get('mqtt_port', '1883'))

        ttk.Button(frame, text="Connect", command=self.connect).grid(column=1, row=9, sticky=tk.E)

        for child in frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def connect(self):
        self.config = {
            'server_address': self.server_address.get(),
            'server_port': self.server_port.get(),
            'api_token': self.api_token.get(),
            'app_id': self.app_id.get(),
            'tenant_id': self.tenant_id.get(),
            'mqtt_broker': self.mqtt_broker.get(),
            'mqtt_port': self.mqtt_port.get()
        }

        try:
            client = ChirpStackClient(
                f"{self.config['server_address']}:{self.config['server_port']}",
                self.config['api_token'],
                self.config['app_id'],
                self.config['tenant_id']
            )
            self.devices = client.list_devices(self.config['app_id'])
            save_config(self.config)
            self.config_complete = True
            self.destroy()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to ChirpStack: {str(e)}")