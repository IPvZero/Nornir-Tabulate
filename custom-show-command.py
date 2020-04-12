from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result
from colorama import Fore, Style
import threading
from tabulate import tabulate
import itertools as it

LOCK = threading.Lock()

def get_facts(task):
    r = task.run(netmiko_send_command, command_string="show ip ospf neighbor", use_textfsm="True")
    b = task.run(netmiko_send_command, command_string="show ip bgp summary", use_textfsm="True")
    c = task.run(netmiko_send_command, command_string="show ip bgp", use_textfsm="True")
    task.host["ospf-neigh"] = r.result
    task.host["bgp-sum"] = b.result
    task.host["ip-bgp"] = c.result
    ospf_data = task.host["ospf-neigh"]
    bgp_data = task.host["bgp-sum"]
    ip_bgp = task.host["ip-bgp"]
    ospf_neigh_list = []
    bgp_neigh_list = []
    remote_as_list = []
    bgp_prefixes_list = []
    bgp_next_hop_list = []
    headers = ["OSPF Neighbor ID", "BGP Neighbor ID", "BGP Neighbor AS", "Learned BGP Prefixes", "BGP Prefix Next Hop"]
    for number in ospf_data:
        ospf_neigh_list.append(number['neighbor_id'])
    for number in bgp_data:
        bgp_neigh_list.append(number['bgp_neigh'])
        remote_as_list.append(number['neigh_as'])
    for number in ip_bgp:
        bgp_prefixes_list.append(number['network'])
        bgp_next_hop_list.append(number['next_hop'])
    LOCK.acquire()
    print("\n")
    print(Fore.GREEN + Style.BRIGHT + "*" * 111)
    print(Fore.YELLOW + f"Routing Information for {task.host}")
    print(Fore.GREEN + Style.BRIGHT + "*" * 111)
    table = it.zip_longest(ospf_neigh_list, bgp_neigh_list, remote_as_list, bgp_prefixes_list, bgp_next_hop_list)
    print(tabulate(table, headers=headers, tablefmt="psql"))
    print(Fore.MAGENTA + Style.BRIGHT + "*" * 111)
    LOCK.release()


def main() -> None:
    nr = InitNornir(config_file="config.yaml")
    result = nr.run(task=get_facts)

if __name__ == '__main__':
    main()
