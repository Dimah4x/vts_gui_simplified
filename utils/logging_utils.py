import os
from datetime import datetime


class Logger:
    def __init__(self, general_log_file="events_log.txt", alert_log_file="alerts_log.txt"):
        self.general_log_file = general_log_file
        self.alert_log_file = alert_log_file
        self.ensure_log_directory()

    def ensure_log_directory(self):
        for log_file in [self.general_log_file, self.alert_log_file]:
            directory = os.path.dirname(log_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

    def log(self, message, is_alert=False):
        timestamp = self.get_time()
        log_entry = f"{timestamp} - {message}"
        print(log_entry)  # Print to console

        log_file = self.alert_log_file if is_alert else self.general_log_file
        with open(log_file, "a") as f:
            f.write(log_entry + "\n")

    def get_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def start_logging(self):
        self.log("Application started")

    def stop_logging(self):
        self.log("Application closed")
        for log_file in [self.general_log_file, self.alert_log_file]:
            with open(log_file, "a") as f:
                f.write("\n" + "=" * 50 + "\n\n")


logger = Logger()  # Create a global logger instance