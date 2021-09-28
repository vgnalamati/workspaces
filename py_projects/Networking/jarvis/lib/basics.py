import getpass
import json
import os
import re
import socket
import subprocess
from functools import wraps
from time import time

import click
from netaddr import IPNetwork, IPAddress
from termcolor import colored
from textfsm import TextFSM


CWD = os.getcwd()


def shell_execute(full_command_string):
    output = {}
    popen_output = subprocess.Popen(
        full_command_string,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )
    (stdout, stderr) = popen_output.communicate()
    output["return_code"] = int(popen_output.returncode)
    output["stderr"] = stderr
    output["stdout"] = stdout
    return output


def read_file(filename_with_path: str) -> object:
    filename = os.path.basename(filename_with_path)
    path = os.path.dirname(filename_with_path)
    extension = filename.split(".")[1]
    if filename in os.listdir(path):
        with open(os.path.join(path, filename), "r+") as raw:
            if extension == "json":
                data = json.load(raw)
            else:
                data = raw.read()
        return data
    else:
        print(f"{filename} not found in {path}")
        return


def ping_test(ip):
    IP = IPNetwork(ip)
    ping_type = "ping"
    if IP.version == 6:
        ping_type = "ping6"
    response = os.system(f"{ping_type} -c 2 {ip}")
    if response == 0:
        return "Success"
    return "Fail"


def is_ipv4(ip):
    return True if IPAddress(ip).version == 4 else False


def is_ipv6(ip):
    return True if IPAddress(ip).version == 6 else False


def get_hostname(ip):
    try:
        output = socket.gethostbyaddr(ip)
        return output[0]
    except socket.herror:
        return "No Hostname"


def multiple_regex_searches(regex_strings, line):
    data = []
    for regex_string in regex_strings:
        data.append(search_and_return_dict(regex_string, line))
    return data


def search_and_return_dict(regex_string, line):
    regex_search = re.search(regex_string, line)
    if regex_search:
        return regex_search.groupdict()
    return None


def execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        func_return = func(*args, **kwargs)
        elapsed_time = time() - start_time
        text = colored(
            "{:.5f} secs".format(elapsed_time),
            "green",
            attrs=["blink"],
        )
        print(f"Total Execution time of {func.__name__} is {text}")
        return func_return

    return wrapper


class ExecutionTime(object):
    def __init__(self, **kwargs):
        self.func_name = kwargs.get("name", None)

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            start_time = time()
            func(*args, **kwargs)
            elapsed_time = time() - start_time
            if not self.func_name:
                self.func_name = func.__name__
            print(
                "Total Execution time of {} is {:.2f} secs".format(
                    self.func_name, elapsed_time
                )
            )

        return wrapper


def scrub_data_with_fsm(raw_data, fsm_file):
    try:
        fsm_file_with_full_path = os.path.join(FSMS_DIR, fsm_file)
        with open(fsm_file_with_full_path, "r") as fsm_data:
            message.info(f"Scrubing Output with {fsm_file}")
            fsm = TextFSM(fsm_data)
        parsed_ouput = fsm.ParseText(raw_data)
        return [dict(zip(fsm.header, output)) for output in parsed_ouput]
    except FileNotFoundError:
        message.fail("FSM file not found in Alfred's Directory")
        return raw_data


class Credentials:
    def __init__(self):
        self.username = (
            input(colored(f"Enter Username (default {os.getlogin()}): ", "yellow"))
            or os.getlogin()
        )
        self.password = getpass.getpass()


class message(object):
    @staticmethod
    def success(message):
        click.echo(
            "{}: {}".format(click.style("[ SUCCESS ]", bg="green", bold=True), message),
            color=True,
        )

    @staticmethod
    def fail(message):
        click.echo(
            "{}: {}".format(click.style("[ ERROR ]", bg="red", bold=True), message),
            color=True,
        )

    @staticmethod
    def info(message):
        click.echo(
            "{}: {}".format(click.style("[ INFO ]", bg="yellow", bold=True), message),
            color=True,
        )

    @staticmethod
    def warning(message):
        click.echo(
            "{}: {}".format(click.style("[ WARNING ]", bg="blue", bold=True), message),
            color=True,
        )

    @staticmethod
    def custom(signal, message):
        click.echo(
            "{}: {}".format(
                click.style(f"[ {signal} ]", bg="cyan", bold=True), message
            ),
            color=True,
        )
