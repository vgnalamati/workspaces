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
    return obj.get_facts()


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


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--device',
        dest='device_name',
        help='Name of the device'
    )
    parser.add_argument(
        '--os',
        dest='os_type',
        choices=['eos', 'junos'],
        help='OS Version of the Network Device(s)',
        required=True
    )
    parser.add_argument(
        '--get',
        dest='operation',
        choices=['arp', 'environ', 'base', 'neigh', 'counters'],
        help='Operation to do on Network Device',
        required=True
    )
    return parser.parse_args()


def main():
    implement_operation(cli())


if __name__ == '__main__':
    main()
