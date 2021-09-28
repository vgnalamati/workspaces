from collections import defaultdict
from treelib import Node, Tree, exceptions
from lib.basics import read_file
from prettytable import PrettyTable


pop_path_table_fwd = PrettyTable()
pop_path_table_fwd.field_names = ["POP's", "HOP COUNT"]

pop_path_table_rev = PrettyTable()
pop_path_table_rev.field_names = ["POP's", "HOP COUNT"]

PATH_TO_NETWORK_MAP = "/Users/goutam/test.json"


class NetworkMap(object):

    map = defaultdict(list)

    def __init__(self, list_of_nodes):
        self.direction = str()
        self.nodes = list_of_nodes
        self.paths = {"forward": [], "reverse": []}

    def add_node(self, node1, node2, bi_directional=True):
        self.map[node1].append(node2)
        if bi_directional:
            self.map[node2].append(node1)

    def _do_path_lookup(self, node, dst_node, device_status, network_path):
        device_status[node] = True
        network_path.append(node)
        if node == dst_node:
            self.paths[self.direction].append(network_path.copy())
        else:
            for next_node in self.map[node]:
                if not device_status[next_node]:
                    self._do_path_lookup(next_node,
                                         dst_node,
                                         device_status,
                                         network_path)
        network_path.pop()
        device_status[node] = False

    def get_possible_paths(self, source, destination):
        device_status = {node: False for node in self.nodes}
        network_path = []
        self._do_path_lookup(source, destination, device_status, network_path)

    def get_possible_paths_between_devices(self, node1, node2, bi_directional):
        self.direction = "forward"
        self.get_possible_paths(node1, node2)
        if bi_directional:
            self.direction = "reverse"
            self.get_possible_paths(node2, node1)


def create_tree(list_of_hops, tree):
    #for idx, node in enumerate(list_of_hops):
    #    try:
    #        tree.create_node(list_of_hops[idx+1], list_of_hops[idx+1], parent=list_of_hops[idx])
    #    except IndexError:
    #        pass
    #    except exceptions.DuplicatedNodeIdError:
    #        pass
    #return tree
    return None


def represent_gathered_data(node1, node2, gathered_dict_data, format):
    tree = Tree()
    tree.create_node(node1, node1.lower())
    for found_path in gathered_dict_data["forward"]:
        pop_path_table_fwd.add_row([found_path, len(found_path)-2])
        create_tree(found_path, tree)
    fwd_tree = tree

    if gathered_dict_data["reverse"]:
        tree = Tree()
        tree.create_node(node2, node2.lower())
        for found_path in gathered_dict_data["reverse"]:
            pop_path_table_rev.add_row([found_path, len(found_path)-2])
            tree = create_tree(found_path, tree)
        rev_tree = tree

    if format == 'table':
        pop_path_table_fwd.sortby = "HOP COUNT"
        print("Paths from {} to {}".format(node1, node2))
        print(pop_path_table_fwd)
        if gathered_dict_data["reverse"]:
            print("Paths from {} to {}".format(node2, node1))
            pop_path_table_rev.sortby = "HOP COUNT"
            print(pop_path_table_rev)

    if format == 'tree':
        print("Paths from {} to {}".format(node1, node2))
        #fwd_tree.show()
        if gathered_dict_data["reverse"]:
            print("Paths from {} to {}".format(node2, node1))
            #rev_tree.show()


def create_network_map(json_file):
    input_map = read_file(json_file)
    network_map = NetworkMap(input_map.keys())
    for node, node_peers in input_map.items():
        for node_peer in node_peers:
            network_map.add_node(node, node_peer, bi_directional=False)
    return network_map


def find_paths(args):
    src = args.source
    dst = args.destination
    map = create_network_map(PATH_TO_NETWORK_MAP)
    map.get_possible_paths_between_devices(src, dst, args.bi_directional)
    represent_gathered_data(src.upper(), dst.upper(), map.paths, args.format)
