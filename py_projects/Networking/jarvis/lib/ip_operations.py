import socket
from netaddr import EUI, IPNetwork
from lib.basics import read_file, shell_execute
from prettytable import PrettyTable
from multiprocessing import Pool

slaac_ip_table = PrettyTable()
slaac_ip_table.field_names = ['MAC', 'SLAAC IP', 'HOSTNAME', 'PING CHECK']

ping_table = PrettyTable()
ping_table.field_names = ['HOSTNAME', 'IP', 'PING STATUS']

MAX_PROCESSES = 50


def ping_test(ip):
    IP = IPNetwork(ip)
    ping_type = "ping"
    if IP.version == 6:
        ping_type = "ping6"
    command = f"{ping_type} -c 2 {ip}"
    output = shell_execute(command)
    if output["return_code"] == 0:
        return "Success"
    return "Fail"


def get_hostname(ip):
    try:
        output = socket.gethostbyaddr(ip)
        return output[0]
    except socket.herror:
        return "No Hostname"


def generate_slaac_ip(args):
    if not any([args.file, args.mac]):
        print('Missing Arguments for MAC address')
        return
    macs = read_file(args.file).splitlines() if args.file else [args.mac]
    mac_pieces_set = gather_mac_pieces(macs)
    prefix_pieces = gather_prefix_pieces(args.prefix)
    status = "-"
    for mac_pieces in mac_pieces_set:
        slaac_ip = eui64_converter(prefix_pieces, mac_pieces)
        try:
            hostname = get_hostname(slaac_ip)
        except Exception:
            hostname = str()
        if args.ping:
            status = ping_test(slaac_ip)
        slaac_ip_table.add_row([':'.join(mac_pieces), slaac_ip, hostname, status])
    print(slaac_ip_table)


def gather_prefix_pieces(prefix: str) -> list:
    pieces = prefix.split(':')
    return pieces[:4] if len(pieces) > 4 else pieces


def gather_mac_pieces(mac_list: list) -> list:
    pieces_list = []
    for mac in mac_list:
        mac = str(EUI(mac)).lower()
        pieces_list.append(mac.split('-'))
    return pieces_list


def eui64_converter(prefix_pieces: list, mac_pieces: list) -> str:
    suffix = []
    for index, piece in enumerate(mac_pieces):
        if index == 0:
            piece = hex(int(piece, 16) ^ 2)[2:]
        if index == 2:
            suffix.append(f"{piece}ff")
        elif index == 3:
            suffix.append(f"fe{piece}")
        elif index % 2 == 0:
            suffix.append("{}{}".format(piece, mac_pieces[index + 1]))
    return ':'.join(prefix_pieces + suffix)


def ping_table_data(ip):
    result = {}
    result['status'] = ping_test(ip)
    result['hostname'] = get_hostname(ip)
    return result


def generate_ping_table(args):
    ips = []
    if args.filename:
        ips = read_file(args.filename).splitlines()
    else:
        net_subnet = IPNetwork(args.subnet)
        ips = [str(ip) for ip in list(net_subnet)]
    if ips:
        pools = Pool(processes=MAX_PROCESSES)
        results = {ip: pools.apply_async(ping_table_data, args=(ip.rstrip(),)) for ip in ips}
        for ip, result in results.items():
            output = result.get()
            ping_table.add_row([output['hostname'], ip, output['status']])
        print(ping_table)
