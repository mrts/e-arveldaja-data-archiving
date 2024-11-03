from pprint import pprint

import yaml

with open('e-arveldaja-openapi.yaml', 'r') as file:
    openapi_data = yaml.safe_load(file)

get_endpoints = []

for path, methods in openapi_data['paths'].items():
    if 'get' in methods:
        get_endpoints.append(f"{path}: {methods['get']['description']}\n\t{methods['get']['responses']['200']['content']['application/json']['schema']}")

get_endpoints.sort()

for line in get_endpoints:
    print(line)

