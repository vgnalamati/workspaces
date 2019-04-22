import os
import json
from jinja2 import Environment, FileSystemLoader
from .defaults import NODES, DEFAULTS
from .custom_jinja_filters import ip_to_addr
#import .custom_jinja_filters

CWD = os.getcwd()


def read_base_file(filename: str) -> dict:
    data = {}
    if filename in os.listdir(f"{CWD}"):
        with open(os.path.join(CWD, filename), "r+") as raw:
            data = json.load(raw)
    else:
        print(f"{filename} not found in {CWD}")
    if data:
        if validate_input_data(data):
            return data
        else:
            print("Invalid Input arguments in YAML file...")


def validate_input_data(data: dict) -> bool:
    print("Validating File data...")
    try:
        tmpl_verification = validate_template(data['template'])
        var_verification = validate_variables(data['variables'])
        if all([tmpl_verification, var_verification]):
            print("Success: Input file passed the checks")
            return True
    except KeyError as e:
        print(f"Missing Key: {e}")
        return False


def validate_template(template_file: str) -> bool:
    if not os.path.isfile(template_file):
        print(f"Template file not found in: {template_file}")
        return False
    return True


def validate_variables(variables: list) -> bool:
    if not isinstance(variables, list):
        print("Variables should be defined in list")
        return False
    return True


def write_to_file(filename: str, data: str) -> None:
    with open(os.path.join(CWD, filename), 'w+') as f:
        f.write(data)
    print(f"Created file {filename} in {CWD}")


def udpate_base_provided_with_defaults(data: dict, model: str) -> dict:
    if model in ['acc', 'agg', 'cor']:
        data.update(DEFAULTS)
    return data


def load_custom_filters(jinja_environment):
    for function in dir(custom_jinja_filters):
        jinja_environment.filters[str(function)] = function
    return jinja_environment


def file_path_and_name(full_path_to_file: str) -> str:
    path = os.path.dirname(full_path_to_file)
    filename = os.path.basename(full_path_to_file)
    return path, filename


def expand(args):
    verified_data = read_base_file(args.var)
    template_dir, template_name = file_path_and_name(verified_data['template'])
    for variable_set in verified_data['variables']:
        variable_set = udpate_base_provided_with_defaults(variable_set, NODES[template_name])
        jinja_env = Environment(loader=FileSystemLoader(template_dir))
        jinja_env.filters['ip_to_addr'] = ip_to_addr
        #jinja_env = load_custom_filters(jinja_env)
        template = jinja_env.get_template(template_name)
        rendered_file = template.render(variable_set)
        write_to_file(variable_set['hostname'], rendered_file)

