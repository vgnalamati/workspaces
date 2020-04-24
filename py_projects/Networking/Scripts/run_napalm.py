#!/usr/bin/env python3

import os
import json
import getpass
import argparse
from napalm import get_network_driver


def do_operation(operation_name):
    return {
        'arp': arp_table,
        'base': base_info
        }.get(operation_name)


def arp_table(device_obj):
    return device_obj.get_arp_table()


def base_info(device_obj):
    return device_obj.get_facts()


def implement_operation(args):
    device_driver = get_network_driver(args.os_type)
    with device_driver(args.device_name, getpass.getuser(), getpass.getpass()) as device:
        print(do_operation(args.operation)(device))


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
        choices=['arp', 'bgp', 'base'],
        help='Operation to do on Network Device',
        required=True
    )
    return parser.parse_args()


def main():
    implement_operation(cli())


if __name__ == '__main__':
    main()
