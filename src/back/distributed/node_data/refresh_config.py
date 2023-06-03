import os
import json

directory = '.'  # Replace with the actual directory path


def update_config_file(file_path):
    with open(file_path, 'r+') as f:
        data = json.load(f)
        for node in data['nodes']:
            node['first_boot'] = True
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def process_directory(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file == 'config.json':
                file_path = os.path.join(root, file)
                update_config_file(file_path)
                print(f'Updated {file_path}')

process_directory(directory)