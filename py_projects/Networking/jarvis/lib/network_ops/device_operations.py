import logging
import os
from itertools import repeat
from multiprocessing import RLock, Pool

import scp
from lib.basics import (
    message,
    scrub_data_with_fsm,
    Credentials,
)
from lib.network_ops.connector import DeviceConnector, get_ssh_connection
from tqdm import tqdm


logger = logging.getLogger(__name__)


def get_device_ouput(args):
    creds = Credentials()
    with DeviceConnector(args.hostname, creds.username, creds.password) as device:
        print(device.send_command(args.cmd))


def scp_process(hostname, creds, filename, dst_file_path, index):
    def tqdm_progress(t):
        last_sent = [0]

        def update_to(filename, size, sent):
            t.total = size
            t.update(sent - last_sent[0])
            last_sent[0] = sent

        return update_to

    logger.info("{}: Starting SCP to {}:".format(os.getpid(), hostname))
    try:
        ssh_conn = get_ssh_connection(hostname, creds.username, creds.password)
        if ssh_conn:
            scp_transport = ssh_conn.get_transport()
            scp_channel = scp_transport.open_session()
            with tqdm(
                unit="b",
                unit_scale=True,
                desc=hostname,
                position=index,
            ) as t:
                scp_connection = scp.SCPClient(
                    scp_transport, progress=tqdm_progress(t), socket_timeout=15
                )
                scp_connection.put(filename, dst_file_path)
            logger.info("SCP Complete for {}".format(hostname))
    except Exception as e:
        logger.critical("Failed SCP. Failed Reason: {}".format(e))
    except KeyboardInterrupt:
        logger.critical("SCP Operation received HUP Signal")
    finally:
        scp_channel.close()
        ssh_conn.close()
    logger.info("Closing SCP Operation on {}".format(hostname))


def scp_operation(args):
    credentials = Credentials()
    targets = args.hostname.split(",")
    tqdm.set_lock(RLock())
    with Pool(initializer=tqdm.set_lock, initargs=(tqdm.get_lock(),)) as pool:
        pool.starmap(
            scp_process,
            zip(
                targets,
                repeat(credentials),
                repeat(args.filename),
                repeat(args.dst_file_path),
                list(range(len(targets))),
            ),
        )
