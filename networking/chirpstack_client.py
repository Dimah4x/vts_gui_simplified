import grpc
from chirpstack_api import api
from google.protobuf.json_format import MessageToDict
from datetime import datetime, timedelta
from utils.logging_utils import logger

class ChirpStackClient:
    def __init__(self, server, api_token, app_id, tenant_id):
        self.server = server
        self.api_token = api_token
        self.app_id = app_id
        self.tenant_id = tenant_id
        self.channel = grpc.insecure_channel(self.server)
        self.device_service = api.DeviceServiceStub(self.channel)
        self.device_profile_service = api.DeviceProfileServiceStub(self.channel)
        logger.log(f"ChirpStack client initialized for server: {server}")

    def _get_metadata(self):
        return [("authorization", f"Bearer {self.api_token}")]

    def list_devices(self, application_id):
        logger.log(f"Fetching devices for application ID: {application_id}")
        req = api.ListDevicesRequest(application_id=application_id, limit=100)
        resp = self.device_service.List(req, metadata=self._get_metadata())
        return [MessageToDict(device) for device in resp.result]

    def get_device_status(self, dev_eui):
        logger.log(f"Getting status for device: {dev_eui}")
        req = api.GetDeviceRequest(dev_eui=dev_eui)
        resp = self.device_service.Get(req, metadata=self._get_metadata())
        device = MessageToDict(resp.device)
        last_seen = device.get('lastSeenAt')
        if last_seen:
            last_seen_dt = datetime.fromtimestamp(int(last_seen.split('.')[0]))
            is_online = datetime.now() - last_seen_dt < timedelta(minutes=10)
        else:
            last_seen_dt = None
            is_online = False
        return {"last_seen": last_seen_dt, "is_online": is_online}

    def enqueue_downlink(self, dev_eui, data, confirmed=True, f_port=10):
        """Enqueue a downlink message to a device."""
        logger.log(f"Enqueueing downlink for device {dev_eui}: {data.hex()}")

        req = api.EnqueueDeviceQueueItemRequest()
        req.queue_item.dev_eui = dev_eui
        req.queue_item.confirmed = confirmed
        req.queue_item.data = data
        req.queue_item.f_port = f_port

        try:
            response = self.device_service.Enqueue(req, metadata=self._get_metadata())
            logger.log(f"Downlink enqueued successfully. Response: {response}")
            return True, "Command enqueued successfully."
        except grpc.RpcError as e:
            error_message = f"Failed to enqueue command: {e.details()}"
            logger.log(error_message)
            return False, error_message
        except Exception as e:
            error_message = f"Unexpected error enqueueing downlink: {str(e)}"
            logger.log(error_message)
            return False, error_message

    def get_device_profiles(self):
        req = api.ListDeviceProfilesRequest(tenant_id=self.tenant_id, limit=100)
        resp = self.device_profile_service.List(req, metadata=self._get_metadata())
        return [MessageToDict(profile) for profile in resp.result]

    def add_device(self, dev_eui, name, device_profile_id, application_id, nwk_key, device_type):
        logger.log(f"Adding new device: {name} ({dev_eui})")
        try:
            device = api.Device(
                dev_eui=dev_eui,
                name=name,
                description=device_type,
                application_id=application_id,
                device_profile_id=device_profile_id
            )
            req = api.CreateDeviceRequest(device=device)
            self.device_service.Create(req, metadata=self._get_metadata())

            # Set device keys
            keys_req = api.CreateDeviceKeysRequest(
                device_keys=api.DeviceKeys(
                    dev_eui=dev_eui,
                    nwk_key=nwk_key
                )
            )
            self.device_service.CreateKeys(keys_req, metadata=self._get_metadata())

            logger.log(f"Device {name} ({dev_eui}) added successfully with keys")
            return True, "Device added successfully"
        except grpc.RpcError as e:
            error_message = f"Failed to add device: {e.details()}"
            logger.log(error_message)
            return False, error_message
        except Exception as e:
            error_message = f"Unexpected error adding device: {str(e)}"
            logger.log(error_message)
            return False, error_message

    def remove_device(self, dev_eui):
        req = api.DeleteDeviceRequest(dev_eui=dev_eui)
        self.device_service.Delete(req, metadata=self._get_metadata())

    def get_alert_log(self):
        # Implement method to retrieve alert log
        # This is a placeholder and should be implemented based on your specific requirements
        return "Alert log placeholder"

    def get_general_log(self):
        # Implement method to retrieve general log
        # This is a placeholder and should be implemented based on your specific requirements
        return "General log placeholder"