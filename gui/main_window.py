import tkinter as tk
from tkinter import ttk, messagebox
from .node_block import NodeBlock
from .node_detail_dialog import NodeDetailDialog
from .scrollable_frame import ScrollableFrame
from .log_window import LogWindow
from .add_node_dialog import AddNodeDialog
from core.node_manager import NodeManager
from networking.mqtt_client import MQTTClient
from utils.logging_utils import logger
import json
from datetime import datetime, timedelta

VERSION = "1.2"


class MainWindow:
    def __init__(self, master, chirpstack_client, devices, mqtt_config):
        self.master = master
        self.chirpstack_client = chirpstack_client
        self.node_manager = NodeManager()
        self.setup_styles()
        self.setup_ui()
        self.node_manager.load_nodes_from_chirpstack(devices)
        self.update_node_layout()  # Update the layout after loading nodes

        self.mqtt_client = MQTTClient(
            mqtt_config['broker'],
            mqtt_config['port'],
            self.handle_mqtt_message
        )
        self.mqtt_client.connect()
        self.node_manager.load_nodes_from_chirpstack(devices)

    def setup_ui(self):
        self.master.title("LoRa Node Management")
        self.master.geometry("800x600")
        self.setup_menu()
        self.setup_node_frame()

    def setup_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh", command=self.refresh_nodes)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

        node_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Node", menu=node_menu)
        node_menu.add_command(label="Add New Node", command=self.add_new_node)
        node_menu.add_command(label="Remove Node", command=self.remove_node_menu)

        logs_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Logs", menu=logs_menu)
        logs_menu.add_command(label="General Log", command=self.show_general_log)
        logs_menu.add_command(label="Alert Log", command=self.show_alert_log)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_node_frame(self):
        self.scrollable_frame = ScrollableFrame(self.master)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)
        self.node_frame = self.scrollable_frame.scrollable_frame
        self.update_node_layout()

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Green.TFrame", background="green")
        style.configure("Gray.TFrame", background="gray")
        style.configure("Red.TFrame", background="red")

    def update_node_layout(self):
        logger.log("Starting update_node_layout")
        logger.log(f"Number of nodes: {len(self.node_manager.get_all_nodes())}")

        for widget in self.node_frame.winfo_children():
            widget.destroy()

        nodes = self.node_manager.get_all_nodes()
        width = self.node_frame.winfo_width()
        node_width = 200  # Adjust as needed
        columns = max(1, width // node_width)

        for i, node in enumerate(nodes):
            row = i // columns
            col = i % columns
            node_block = NodeBlock(self.node_frame, node, self.on_node_click)
            node_block.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            node_block.bind('<<NodeClicked>>', self.on_node_click)
            node_block.bind('<<NodeRightClicked>>', self.on_node_right_click)
            logger.log(f"Created block for node: {node.name} (Status: {node.status})")

        for i in range(columns):
            self.node_frame.columnconfigure(i, weight=1)
        self.node_frame.rowconfigure("all", weight=1)

        logger.log(f"Finished update_node_layout. Displayed {len(nodes)} nodes.")

        # Force redraw
        self.master.update_idletasks()
        current_geometry = self.master.geometry()
        self.master.geometry(f"{self.master.winfo_width() + 1}x{self.master.winfo_height()}")
        self.master.geometry(current_geometry)
        logger.log("Finished update_node_layout")

    def on_node_click(self, event):
        node = event.widget.node
        if node.has_alert:
            node.clear_alert()
            self.update_node_block(node)
        self.open_node_detail(node)

    def on_node_right_click(self, event):
        node = event.widget.node
        self.show_context_menu(event, node)

    def show_context_menu(self, event, node):
        context_menu = tk.Menu(self.master, tearoff=0)
        context_menu.add_command(label="Remove Node", command=lambda: self.remove_node(node))
        context_menu.tk_popup(event.x_root, event.y_root)
        context_menu.grab_release()

    def remove_node_menu(self):
        nodes = self.node_manager.get_all_nodes()
        if not nodes:
            messagebox.showinfo("No Nodes", "There are no nodes to remove.")
            return

        node_names = [node.name for node in nodes]
        selected_name = tk.StringVar(self.master)
        selected_name.set(node_names[0])  # Set the default option

        dialog = tk.Toplevel(self.master)
        dialog.title("Remove Node")
        dialog.geometry("300x100")

        ttk.Label(dialog, text="Select node to remove:").pack(pady=5)
        option_menu = ttk.OptionMenu(dialog, selected_name, *node_names)
        option_menu.pack(pady=5)

        ttk.Button(dialog, text="Remove", command=lambda: self.remove_selected_node(selected_name.get(), dialog)).pack(
            pady=5)

    def remove_selected_node(self, node_name, dialog):
        node = next((node for node in self.node_manager.get_all_nodes() if node.name == node_name), None)
        if node:
            self.remove_node(node)
        dialog.destroy()

    def remove_node(self, node):
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove the node {node.name}?"):
            try:
                self.chirpstack_client.remove_device(node.dev_eui)
                self.node_manager.remove_node(node.dev_eui)
                logger.log(f"Node {node.name} ({node.dev_eui}) removed successfully")
                messagebox.showinfo("Success", f"Node {node.name} removed successfully.")
                self.update_node_layout()
            except Exception as e:
                error_message = f"Failed to remove node {node.name}: {str(e)}"
                logger.log(error_message)
                messagebox.showerror("Error", error_message)

    def show_general_log(self):
        LogWindow(self.master, "General Log", "general")

    def show_alert_log(self):
        LogWindow(self.master, "Alert Log", "alert")

    def open_node_detail(self, node):
        logger.log(f"Opening detail dialog for node: {node.name}")
        NodeDetailDialog(self.master, node, self.chirpstack_client)

    def add_new_node(self):
        dialog = AddNodeDialog(self.master, self.chirpstack_client, self.node_manager)
        self.master.wait_window(dialog)

        logger.log(f"Dialog closed. Checking if node was added.")

        if hasattr(dialog, 'node_added') and dialog.node_added:
            logger.log(f"New node added: {dialog.added_node.name}")
            logger.log(f"Number of nodes before update: {len(self.node_manager.get_all_nodes())}")
            self.update_node_layout()
            logger.log(f"Number of nodes after update: {len(self.node_manager.get_all_nodes())}")
            logger.log("Node layout updated with new node")
        else:
            logger.log("No new node was added.")

    def refresh_nodes(self):
        try:
            devices = self.chirpstack_client.list_devices(self.chirpstack_client.app_id)
            self.node_manager.load_nodes_from_chirpstack(devices)
            self.update_node_layout()
            logger.log("Node layout refreshed")

            # Check for offline nodes
            current_time = datetime.now()
            for node in self.node_manager.get_all_nodes():
                if node.last_seen and isinstance(node.last_seen, datetime):
                    if (current_time - node.last_seen) > timedelta(minutes=10):
                        node.set_offline()
                        self.update_node_block(node)
                else:
                    logger.log(f"Node {node.name} has invalid last_seen value: {node.last_seen}")
        except Exception as e:
            logger.log(f"Error refreshing nodes: {str(e)}")

    def show_about(self):
        message = f"LoRa Node Management\nVersion {VERSION}\n© Avi Bents 2024"
        messagebox.showinfo("About", message)

    def handle_mqtt_message(self, topic: str, payload: dict):
        logger.log(f"Received MQTT message on topic: {topic}")
        event_type = topic.split('/')[-1]

        if event_type == "up":
            self.handle_uplink(payload)
        elif event_type == "join":
            self.handle_join(payload)
        elif event_type == "status":
            self.handle_status(payload)
        elif event_type == "ack":
            self.handle_ack(payload)
        elif event_type == "txack":
            self.handle_txack(payload)
        elif event_type == "log":
            self.handle_log(payload)
        else:
            logger.log(f"Unknown event type: {event_type}")

    def handle_uplink(self, data):
        device_name = data['deviceInfo'].get('deviceName', 'Unknown device')
        dev_eui = data['deviceInfo'].get('devEui', 'Unknown DevEUI')
        message = data.get('object', {}).get('message', 'No message')
        rssi = data['rxInfo'][0]['rssi'] if 'rxInfo' in data and len(data['rxInfo']) > 0 else 'N/A'
        snr = data['rxInfo'][0]['snr'] if 'rxInfo' in data and len(data['rxInfo']) > 0 else 'N/A'

        node = self.node_manager.get_node(dev_eui)
        if node:
            logger.log(f"Handling uplink for node: {node.name}")
            node.update_last_seen()
            if "Alert" in message:
                node.set_alert()
                self.handle_alert(node, message)
            elif not node.has_alert:  # Only update status if there's no active alert
                node.update_status("Online", datetime.now(), rssi, snr)
                self.handle_normal_uplink(node, message)

            self.update_node_block(node)
            logger.log(f"Node block updated for {node.name}")
        else:
            logger.log(f"Node not found for DevEUI: {dev_eui}")

        self.update_rssi_snr(rssi, snr)

        timestamp = self.get_time()
        event_info = f"{timestamp} - Uplink - Device: {device_name}, RSSI: {rssi}, SNR: {snr}, Message: {message}"
        self.add_event_to_listbox(event_info)

    def handle_alert(self, node, message):
        alert_info = f"Alert triggered by device {node.name} - {message}"
        self.add_alert_to_listbox(alert_info)

        # Send 0xFF to Sound Unit and Wearable Alert Unit devices
        for alert_node in self.node_manager.get_all_nodes():
            if alert_node.device_type in ["Sound Unit", "Wearable Alert Unit", "LiDAR unit"]:
                self.chirpstack_client.enqueue_downlink(alert_node.dev_eui, bytes([0xFF]))
                timestamp = self.get_time()
                event_info = f"{timestamp} - Downlink sent to device {alert_node.name} - {alert_node.dev_eui}, [0xFF] - Alert Response"
                self.add_event_to_listbox(event_info)

    def handle_normal_uplink(self, node, message):
        uplink_info = f"Uplink received from device {node.name} - {message}"
        self.add_event_to_listbox(uplink_info)

    def handle_status_message(self, device_name, message):
        status_info = f"Status message from device {device_name} - {message}"
        self.add_alert_to_listbox(status_info)

    def handle_data_message(self, device_name, message):
        data_info = f"Data message from device {device_name} - {message}"
        self.add_alert_to_listbox(data_info)

    def handle_reset_message(self, device_name, message):
        reset_info = f"Reset message from device {device_name} - {message}"
        self.add_alert_to_listbox(reset_info)

    def handle_join(self, data):
        device_name = data['deviceInfo'].get('deviceName', 'Unknown device')
        dev_eui = data['deviceInfo'].get('devEui', 'Unknown DevEUI')

        timestamp = self.get_time()
        event_info = f"{timestamp} - Join - Device: {device_name}, DevEUI: {dev_eui}"
        self.add_event_to_listbox(event_info)

    def handle_status(self, data):
        device_name = data['deviceInfo'].get('deviceName', 'Unknown device')
        margin = data.get('margin', 'N/A')
        battery = data.get('batteryLevel', 'N/A')
        external_power = data.get('externalPowerSource', False)
        last_seen = data.get('lastSeenAt', 'N/A')

        timestamp = self.get_time()
        event_info = f"{timestamp} - Status - Device: {device_name}, Margin: {margin}, Battery: {battery}, External Power: {external_power}, Last Seen: {last_seen}"
        self.add_event_to_listbox(event_info)

    def handle_ack(self, data):
        device_name = data['deviceInfo'].get('deviceName', 'Unknown device')
        acknowledged = data.get('acknowledged', False)

        timestamp = self.get_time()
        event_info = f"{timestamp} - ACK - Device: {device_name}, Acknowledged: {acknowledged}"
        self.add_event_to_listbox(event_info)

    def handle_txack(self, data):
        device_name = data['deviceInfo'].get('deviceName', 'Unknown device')

        timestamp = self.get_time()
        event_info = f"{timestamp} - TXACK - Device: {device_name}"
        self.add_event_to_listbox(event_info)

    def handle_log(self, data):
        device_name = data['deviceInfo'].get('deviceName', 'Unknown device')
        log_message = data.get('message', 'No message')
        level = data.get('level', 'Unknown level')

        timestamp = self.get_time()
        event_info = f"{timestamp} - Log - Device: {device_name}, Level: {level}, Message: {log_message}"
        self.add_event_to_listbox(event_info)

    def get_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_rssi_snr(self, rssi, snr):
        # Update RSSI and SNR labels in the UI
        if hasattr(self, 'rssi_label'):
            self.rssi_label.config(text=f"RSSI: {rssi}")
        if hasattr(self, 'snr_label'):
            self.snr_label.config(text=f"SNR: {snr}")

    def add_event_to_listbox(self, event_info):
        self.master.after(0, lambda: self._add_event_to_listbox(event_info))

    def _add_event_to_listbox(self, event_info):
        if hasattr(self, 'log_listbox'):
            self.log_listbox.insert(tk.END, event_info)
            self.log_listbox.see(tk.END)
        logger.log(event_info)

    def add_alert_to_listbox(self, alert_info):
        self.master.after(0, lambda: self._add_alert_to_listbox(alert_info))

    def _add_alert_to_listbox(self, alert_info):
        if hasattr(self, 'alert_listbox'):
            self.alert_listbox.insert(tk.END, alert_info)
            self.alert_listbox.see(tk.END)
        logger.log(alert_info, is_alert=True)

    def update_node_block(self, node):
        for widget in self.node_frame.winfo_children():
            if isinstance(widget, NodeBlock) and widget.node.dev_eui == node.dev_eui:
                logger.log(f"Updating node block for {node.name}. Current status: {node.status}")
                widget.node = node  # Update the node reference
                widget.update_display()
                logger.log(f"Node block updated for {node.name}")
                break
        else:
            logger.log(f"Node block not found for {node.name}")

    def on_closing(self):
        self.mqtt_client.disconnect()
        logger.log("MQTT client disconnected")

    def check_offline_nodes(self):
        try:
            for node in self.node_manager.get_all_nodes():
                if not node.is_online():
                    node.set_offline()
                    self.update_node_block(node)
        except Exception as e:
            logger.log(f"Error checking offline nodes: {str(e)}")
        finally:
            self.master.after(60000, self.check_offline_nodes)  # Check every minute