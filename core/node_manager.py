from .end_node import EndNode
from utils.logging_utils import logger


class NodeManager:
    def __init__(self):
        self.nodes = {}

    def load_nodes_from_chirpstack(self, devices):
        self.nodes = {}
        logger.log(f"Loading {len(devices)} devices from ChirpStack")
        for device in devices:
            dev_eui = device['devEui']
            name = device['name']
            device_type = device.get('description', 'Unknown')
            last_seen = device.get('lastSeenAt')
            node = EndNode(dev_eui, name, device_type)
            if last_seen:
                node.update_status("Online" if node.is_online() else "Offline", last_seen)
            else:
                node.update_status("Never seen", None)
            self.nodes[dev_eui] = node
            logger.log(f"Loaded node: {name} (EUI: {dev_eui}, Type: {device_type}, Last seen: {last_seen})")
        logger.log(f"Finished loading {len(self.nodes)} nodes")

    def get_device_type(self, device):
        return device.get('description', 'Blank Unit')

    def get_all_nodes(self):
        return list(self.nodes.values())

    def add_node(self, dev_eui, name, device_type):
        node = EndNode(dev_eui=dev_eui, name=name, device_type=device_type)
        self.nodes[dev_eui] = node
        logger.log(f"Node {name} ({dev_eui}) added to NodeManager")
        return node

    def remove_node(self, dev_eui):
        if dev_eui in self.nodes:
            node = self.nodes.pop(dev_eui)
            logger.log(f"Node {node.name} ({dev_eui}) removed from NodeManager")
        else:
            logger.log(f"Attempted to remove non-existent node: {dev_eui}")

    def get_node(self, dev_eui):
        return self.nodes.get(dev_eui)

    def update_node_status(self, dev_eui, status, last_seen, rssi=None, snr=None):
        if dev_eui in self.nodes:
            self.nodes[dev_eui].update_status(status, last_seen, rssi, snr)