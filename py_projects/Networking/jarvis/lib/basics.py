import re
import os
import json
import socket
import subprocess
from netaddr import IPNetwork

CWD = os.getcwd()

def shell_execute(full_command_string):
    output = {}
    popen_output = subprocess.Popen(full_command_string,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              shell=True)
    (stdout, stderr) = popen_output.communicate()
    output["return_code"] = int(popen_output.returncode)
    output["stderr"] = stderr
    output["stdout"] = stdout
    return output


def read_file(filename_with_path: str) -> object:
    filename = os.path.basename(filename_with_path)
    path = os.path.dirname(filename_with_path)
    extension=filename.split('.')[1]
    if filename in os.listdir(path):
        with open(os.path.join(path, filename), "r+") as raw:
            if extension == 'json':
                data = json.load(raw)
            else:
                data = raw.read()
        return data
    else:
        print(f"{filename} not found in {path}")
        return
