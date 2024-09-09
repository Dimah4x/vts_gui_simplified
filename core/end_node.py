from datetime import datetime, timedelta
from utils.logging_utils import logger


class EndNode:
    def __init__(self, dev_eui, name, device_type):
        self.dev_eui = dev_eui
        self.name = name
        self.device_type = device_type
        self.status = "Unknown"
        self.last_seen = None
        self.rssi = None
        self.snr = None
        self.has_alert = False

    def update_status(self, status, last_seen, rssi=None, snr=None):
        old_status = self.status
        if not self.has_alert:  # Only update status if there's no active alert
            self.status = status
        self.last_seen = last_seen
        self.rssi = rssi
        self.snr = snr
        logger.log(f"Node {self.name} status updated: {old_status} -> {self.status} (Alert: {self.has_alert})")

    def update_last_seen(self):
        self.last_seen = datetime.now()
        if not self.has_alert:
            old_status = self.status
            self.status = "Online"
            logger.log(f"Node {self.name} last seen updated. Status: {old_status} -> {self.status}")

    def set_alert(self):
        self.has_alert = True
        old_status = self.status
        self.status = "Alert"
        logger.log(f"Node {self.name} set to alert. Status: {old_status} -> {self.status}")

    def clear_alert(self):
        self.has_alert = False
        old_status = self.status
        self.status = "Online" if self.is_online() else "Offline"
        logger.log(f"Node {self.name} alert cleared. Status: {old_status} -> {self.status}")

    def is_online(self):
        if self.last_seen is None:
            return False
        return datetime.now() - self.last_seen < timedelta(minutes=10)

    def set_offline(self):
        if not self.has_alert:
            old_status = self.status
            self.status = "Offline"
            logger.log(f"Node {self.name} set to offline. Status: {old_status} -> {self.status}")


def __str__(self):
    return self.name