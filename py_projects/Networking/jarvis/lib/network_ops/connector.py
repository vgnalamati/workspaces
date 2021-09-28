import logging

import paramiko
from lib.basics import (
    message,
    scrub_data_with_fsm,
    Credentials,
)
from netmiko import ConnectHandler, SSHDetect
from tenacity import retry, stop_after_attempt, wait_fixed
from yaspin import yaspin

logger = logging.getLogger(__name__)

logging.getLogger("paramiko").setLevel(logging.WARN)

class DeviceConnector(object):
    def __init__(self, device, username, password, vendor="autodetect"):
        self.device = device
        self.vendor = vendor
        self.username = username
        self.password = password
        self.device_data = {
            "device_type": self.vendor,
            "host": self.device,
            "username": self.username,
            "password": self.password,
        }

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
    def __enter__(self):
        try:
            self.get_vendor()
            with yaspin(
                text=f"Connecting: {self.device}",
                color="yellow",
            ) as spinner:
                self.connection = ConnectHandler(**self.device_data)
                if self.connection.is_alive():
                    logger.info(f"Connected to {self.device}")
                    spinner.text = f"{self.device}"
                    spinner.color = "green"
                    spinner.ok("Connected:")
            return self
        except Exception:
            message.fail("Connection Failed")
            logger.critical(f"{self.device} connection failed")
            pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.connection:
                with yaspin(
                    text=f"Disconnecting: {self.device}", color="red"
                ) as spinner:
                    self.connection.disconnect()
                    if not self.connection.is_alive():
                        spinner.text = f"{self.device}"
                        spinner.ok("Disconnected:")
        except Exception:
            None

    def send_command(self, command, use_fsm_file=""):
        message.info(f"Sending Command: {command}")
        logger.info(f"Sending Command: {command}")
        command_output = self.connection.send_command_timing(command)
        if use_fsm_file:
            return scrub_data_with_fsm(
                command_output,
                use_fsm_file,
            )
        return command_output

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
    def get_vendor(self):
        if self.device_data["device_type"] == "autodetect":
            message.info(f"Finding the vendor for the host: {self.device}")
            self.vendor = SSHDetect(**self.device_data).autodetect()
        message.success(f"Identified {self.device} as {self.vendor}")
        self.device_data["device_type"] = self.vendor


def get_ssh_connection(hostname, username, credential):
    try:
        ssh_session = paramiko.SSHClient()
        ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_session.connect(
            hostname,
            username=username,
            password=credential,
            allow_agent=False,
            look_for_keys=False,
        )
    except paramiko.ssh_exception.AuthenticationException:
        print("Authentication failed.")
    return ssh_session
