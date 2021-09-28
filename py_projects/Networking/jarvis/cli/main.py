import argparse
import os

from lib.mapper.network_map import find_paths
from lib.network_ops.device_operations import get_device_ouput, scp_operation
from lib.network_ops.ip_operations import generate_slaac_ip, generate_ping_table
from lib.renderer.template_expand import expand as expand_configs


def cli():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    subparsers.required = True

    default_parent_parser = argparse.ArgumentParser(add_help=False)

    default_parent_parser.add_argument(
        "--execute", action="store_true", dest="execute", help="Real Time Execution"
    )

    configs_expand_parse = subparsers.add_parser(
        "expand", help="expand the variables with template"
    )

    configs_expand_parse.add_argument(
        "--json", dest="var", required=True, help="Json file location"
    )

    eui64_parser = subparsers.add_parser("slaac_ip", help="Generate SLAAC IP")

    eui64_parser.add_argument(
        "--mac", dest="mac", default=None, help="MAC address of the host"
    )

    eui64_parser.add_argument(
        "--file", dest="file", default=None, help="MAC addresses list in a file"
    )

    eui64_parser.add_argument(
        "--prefix",
        dest="prefix",
        required=True,
        help="Prefix Allocated for the Network",
    )

    eui64_parser.add_argument("--ping", dest="ping", action="store_true", default=False)

    ping_table = subparsers.add_parser("ping", help="Ping Sweep given IPs in a File")

    ping_table.add_argument(
        "--file", dest="filename", type=check_file_exist, help="File containing ips"
    )

    ping_table.add_argument(
        "--subnet", dest="subnet", default=None, help="Subnet With mask"
    )

    network_paths = subparsers.add_parser("get_paths", help="Get Network Paths")

    network_paths.add_argument(
        "--src", dest="source", required=True, help="Source Device"
    )

    network_paths.add_argument(
        "--dst", dest="destination", required=True, help="Destination device"
    )

    network_paths.add_argument(
        "--avoid-reverse",
        dest="bi_directional",
        action="store_false",
        help="Destination device",
    )

    network_paths.add_argument(
        "--format",
        dest="format",
        choices={"table", "tree"},
        default="table",
        help="Destination device",
    )

    scp = subparsers.add_parser("scp", help="SCP to a network device")

    scp.add_argument(
        "--target",
        dest="hostname",
        required=True,
        help="Target Hostname to SCP the file. Multiple targets are separated by comma",
    )

    scp.add_argument(
        "--filename",
        dest="filename",
        type=check_file_exist,
        required=True,
        help="Source of File with Path",
    )

    scp.add_argument(
        "--dst",
        dest="dst_file_path",
        required=True,
        help="Path at Destinattion for copying the file",
    )

    send_cmd = subparsers.add_parser(
        "send",
        help="Send Show Command to Network Device",
    )

    send_cmd.add_argument(
        "--device", dest="hostname", required=True, help="Hostname of the device"
    )

    send_cmd.add_argument("--cmd", dest="cmd", required=True, help="Command to send")

    configs_expand_parse.set_defaults(func=expand_configs)
    eui64_parser.set_defaults(func=generate_slaac_ip)
    ping_table.set_defaults(func=generate_ping_table)
    network_paths.set_defaults(func=find_paths)
    scp.set_defaults(func=scp_operation)
    send_cmd.set_defaults(func=get_device_ouput)

    return parser.parse_args()


def check_file_exist(value):
    file_path = os.path.dirname(value)
    file_name = os.path.basename(value)
    if not file_path:
        file_path = CWD
    if file_name not in os.listdir(file_path):
        raise argparse.ArgumentTypeError(
            "{} not found in {}".format(file_name, file_path)
        )
    return value
