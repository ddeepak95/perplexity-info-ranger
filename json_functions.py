import json

def pretty_print(data):
    print(json.dumps(data, indent=2))

def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def parse_string_to_json(string):
    try:
        # Replace single quotes with double quotes
        corrected_string = string.replace("'", '"')
        return json.loads(corrected_string)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def read_json(filename):
    with open(filename) as f:
        return json.load(f)