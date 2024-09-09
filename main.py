import tkinter as tk
from config.settings import load_config
from gui.config_dialog import ConfigDialog
from gui.main_window import MainWindow
from networking.chirpstack_client import ChirpStackClient
from utils.logging_utils import logger


def main():
    logger.start_logging()

    root = tk.Tk()
    root.withdraw()  # Hide the main window initially

    config = load_config()
    config_dialog = ConfigDialog(root, config)
    root.wait_window(config_dialog)

    if config_dialog.config_complete:
        logger.log("Configuration completed successfully")
        chirpstack_client = ChirpStackClient(
            f"{config_dialog.config['server_address']}:{config_dialog.config['server_port']}",
            config_dialog.config['api_token'],
            config_dialog.config['app_id'],
            config_dialog.config['tenant_id']
        )

        mqtt_config = {
            'broker': config_dialog.config['mqtt_broker'],
            'port': int(config_dialog.config['mqtt_port'])
        }

        root.deiconify()  # Show the main window
        main_window = MainWindow(root, chirpstack_client, config_dialog.devices, mqtt_config)
        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, main_window))
        root.mainloop()
    else:
        logger.log("Configuration cancelled")
        root.destroy()  # Exit if configuration was cancelled


def on_closing(root, main_window):
    main_window.on_closing()
    logger.stop_logging()
    root.destroy()


if __name__ == "__main__":
    main()