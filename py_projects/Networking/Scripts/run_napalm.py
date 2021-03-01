#!/usr/bin/env python3

import json
import getpass
import argparse
from napalm import get_network_driver


def do_operation(operation_name):
    return {
        'arp': arp_table,
        'base': base_info,
        'environ': environment_details,
        'neigh': lldp_neighbors,
        'counters': iface_counters,
        }.get(operation_name)


def arp_table(obj):
    return obj.get_arp_table()


def base_info(obj):
    return obj.get_config()


def environment_details(obj):
    return obj.get_environment()


def lldp_neighbors(obj):
    return obj.get_lldp_neighbors()


def iface_counters(obj):
    return obj.get_interfaces_counters()


def implement_operation(args):
    device_driver = get_network_driver(args.os_type)
    with device_driver(args.device_name, getpass.getuser(), getpass.getpass()) as device:
        print(json.dumps(do_operation(args.operation)(device), indent=4))

def push_config(args):
    device_driver = get_network_driver(args.os_type)
    with device_driver(args.device_name, getpass.getuser(), getpass.getpass()) as device:
        device.load_replace_candidate(filename=args.config_file)
        print(device.compare_config())
        device.commit_config()

def cli():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    subparsers.required = True

    default_parent_parser = argparse.ArgumentParser(add_help=False)

    default_parent_parser.add_argument(
        '--device',
        dest='device_name',
        help='Name of the device'
    )
    default_parent_parser.add_argument(
        '--os',
        dest='os_type',
        choices=['eos', 'junos', 'nxos'],
        help='OS Version of the Network Device(s)',
        required=True
    )

    operations_parse = subparsers.add_parser(
        'get',
        parents=[default_parent_parser],
        help='Pull data from devices'
    )

    operations_parse.add_argument(
        '--type',
        dest='operation',
        choices=['arp', 'environ', 'base', 'neigh', 'counters'],
        help='Operations to do on Network Device',
        required=True
    )

    config_changes_parser = subparsers.add_parser(
        'push',
        parents=[default_parent_parser],
        help='Push Config to devices'
    )

    config_changes_parser.add_argument(
        '--file',
        dest='config_file',
        help='Filename with path to push to the device',
        required=True
    )
    operations_parse.set_defaults(func=implement_operation)
    config_changes_parser.set_defaults(func=push_config)

    return parser.parse_args()


def main():
    args = cli()
    args.func(args)


if __name__ == '__main__':
    main()
