import os
import argparse
from lib import expand as expand_configs
from lib.ip_operations import generate_slaac_ip, generate_ping_table
from lib.network_map import find_paths


def cli():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    subparsers.required = True

    default_parent_parser = argparse.ArgumentParser(add_help=False)

    default_parent_parser.add_argument(
        '--execute',
        action='store_true',
        dest='execute',
        help='Real Time Execution'
    )

    configs_expand_parse = subparsers.add_parser(
        'expand',
        help='expand the variables with template'
    )

    configs_expand_parse.add_argument(
        '--json',
        dest='var',
        required=True,
        help='Json file location'
    )

    eui64_parser = subparsers.add_parser(
        'slaac_ip',
        help='Generate SLAAC IP'
    )

    eui64_parser.add_argument(
        '--mac',
        dest='mac',
        default=None,
        help='MAC address of the host'
    )

    eui64_parser.add_argument(
        '--file',
        dest='file',
        default=None,
        help='MAC addresses list in a file'
    )

    eui64_parser.add_argument(
        '--prefix',
        dest='prefix',
        required=True,
        help='Prefix Allocated for the Network'
    )

    eui64_parser.add_argument(
        '--ping',
        dest='ping',
        action='store_true',
        default=False
    )

    ping_table = subparsers.add_parser(
        "ping",
        help="Ping Sweep given IPs in a File"
    )

    ping_table.add_argument(
        '--file',
        dest='filename',
        type=check_file_exist,
        help='File containing ips'
    )

    ping_table.add_argument(
        '--subnet',
        dest='subnet',
        default=None,
        help='Subnet With mask'
    )

    network_paths = subparsers.add_parser(
        "get_paths",
        help="Get Network Paths"
    )

    network_paths.add_argument(
        '--src',
        dest='source',
        required=True,
        help='Source Device'
    )

    network_paths.add_argument(
        '--dst',
        dest='destination',
        required=True,
        help='Destination device'
    )

    network_paths.add_argument(
        '--avoid-reverse',
        dest='bi_directional',
        action='store_false',
        help='Destination device'
    )

    network_paths.add_argument(
        '--max-hops',
        dest='max_hops',
        type=int,
        default=None,
        help='Get all network paths upto given maximum number of \
              Hops in between source and destination'
    )

    network_paths.add_argument(
        '--max-cost',
        dest='max_cost',
        type=int,
        default=None,
        help='Get all network paths upto given maximum OSPF \
              cost in between source and destination'
    )

    network_paths.add_argument(
        '--format',
        dest='format',
        choices={"table", "tree"},
        default='table',
        help='Destination device'
    )

    configs_expand_parse.set_defaults(func=expand_configs)
    eui64_parser.set_defaults(func=generate_slaac_ip)
    ping_table.set_defaults(func=generate_ping_table)
    network_paths.set_defaults(func=find_paths)

    return parser.parse_args()


def check_file_exist(value):
    file_path = os.path.dirname(value)
    file_name = os.path.basename(value)
    if not file_path:
        file_path = CWD
    if file_name not in os.listdir(file_path):
        raise argparse.ArgumentTypeError("{} not found in {}".format(file_name, file_path))
    return value
