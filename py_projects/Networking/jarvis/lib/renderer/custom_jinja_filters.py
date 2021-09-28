from netaddr import IPNetwork


def caps(string):
    return string.upper()


def ip_to_addr(subnet):
    ip = IPNetwork(subnet)
    return f"{ip.ip} {ip.netmask}"


def addresses_list(subnet):
    return [ip for ip in IPNetwork(subnet)]
